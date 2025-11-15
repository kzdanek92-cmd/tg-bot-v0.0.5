"""
Tasks Handler
Обработчик команд для работы с заданиями
"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.task_service import TaskService
from services.user_service import UserService
from keyboards.inline_keyboards import get_tasks_keyboard, get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()


async def cmd_tasks(message: Message, task_service: TaskService, user_service: UserService):
    """
    Обработчик команды /tasks
    
    Показывает список доступных заданий
    """
    user_id = message.from_user.id
    
    try:
        # Проверяем регистрацию
        is_registered = await user_service.is_user_registered(user_id)
        
        if not is_registered:
            await message.answer(
                "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
            )
            return
        
        # Получаем список заданий
        tasks = task_service.get_all_tasks()
        
        if not tasks:
            await message.answer(
                "📭 Пока нет доступных заданий. Загляните позже!",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        tasks_text = f"""
📋 <b>Доступные задания ({len(tasks)})</b>

Выберите задание, чтобы увидеть детали и откликнуться:
"""
        
        await message.answer(
            tasks_text,
            reply_markup=get_tasks_keyboard(tasks),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} просмотрел список заданий")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_tasks для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Ошибка получения списка заданий. Попробуйте позже."
        )


async def cmd_respond(message: Message, task_service: TaskService, user_service: UserService):
    """
    Обработчик команды /respond <task_id>
    
    Обратная совместимость с версией 0.0.1
    """
    user_id = message.from_user.id
    
    try:
        # Проверяем регистрацию
        is_registered = await user_service.is_user_registered(user_id)
        
        if not is_registered:
            await message.answer(
                "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
            )
            return
        
        # Парсим task_id из команды
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(
                "❌ Укажите ID задания!\n"
                "Пример: /respond 1\n\n"
                "Или используйте /tasks для просмотра заданий с кнопками."
            )
            return
        
        try:
            task_id = int(parts[1])
        except ValueError:
            await message.answer("❌ ID задания должен быть числом!")
            return
        
        # Проверяем существование задания
        task = task_service.get_task_by_id(task_id)
        if not task:
            await message.answer(f"❌ Задание с ID {task_id} не найдено!")
            return
        
        # Проверяем, не откликался ли уже
        has_responded = await task_service.has_user_responded(user_id, task_id)
        if has_responded:
            await message.answer("⚠️ Вы уже откликались на это задание!")
            return
        
        # Создаем отклик
        response = await task_service.create_response(user_id, task_id)
        user = await user_service.get_user_profile(user_id)
        
        success_text = f"""
✅ <b>Отклик отправлен!</b>

<b>Задание:</b> {task['title']}

<b>Ваш отклик:</b>
<i>{response.response_text}</i>

💰 <b>Заработано:</b> +{response.earned}₽
💳 <b>Текущий баланс:</b> {user.balance}₽

Продолжайте в том же духе! 🚀
"""
        
        await message.answer(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} откликнулся на задание {task_id} через команду")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_respond для пользователя {user_id}: {e}")
        await message.answer(
            f"😔 Ошибка при отправке отклика: {str(e)}"
        )


async def cmd_my_responses(message: Message, task_service: TaskService, user_service: UserService):
    """
    Обработчик команды /my_responses
    
    Показывает историю откликов пользователя
    """
    user_id = message.from_user.id
    
    try:
        # Проверяем регистрацию
        is_registered = await user_service.is_user_registered(user_id)
        
        if not is_registered:
            await message.answer(
                "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
            )
            return
        
        # Получаем отклики
        responses = await task_service.get_user_responses(user_id)
        
        if not responses:
            await message.answer(
                "📭 У вас пока нет откликов.\n"
                "Используйте /tasks чтобы посмотреть доступные задания!",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Формируем текст с откликами
        responses_text = f"📜 <b>История ваших откликов ({len(responses)}):</b>\n\n"
        
        for idx, resp in enumerate(responses[:10], 1):  # Показываем последние 10
            timestamp = resp.created_at.strftime("%d.%m.%Y %H:%M") if resp.created_at else "Неизвестно"
            responses_text += f"<b>{idx}. {resp.task_title}</b>\n"
            responses_text += f"📅 {timestamp}\n"
            responses_text += f"💬 <i>{resp.response_text[:100]}...</i>\n"
            responses_text += f"💰 Заработано: {resp.earned}₽\n"
            responses_text += "─" * 30 + "\n\n"
        
        user = await user_service.get_user_profile(user_id)
        responses_text += f"\n💳 <b>Общий баланс:</b> {user.balance}₽"
        
        await message.answer(
            responses_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} просмотрел историю откликов")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_my_responses для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Ошибка получения истории откликов. Попробуйте позже."
        )


def register_handlers(router: Router):
    """Регистрация обработчиков tasks handler"""
    router.message.register(cmd_tasks, Command("tasks"))
    router.message.register(cmd_respond, Command("respond"))
    router.message.register(cmd_my_responses, Command("my_responses"))
