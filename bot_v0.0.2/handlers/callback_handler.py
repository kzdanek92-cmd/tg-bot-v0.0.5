"""
Callback Handler
Обработчик всех inline кнопок (callbacks)
"""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from services.user_service import UserService
from services.task_service import TaskService
from keyboards.inline_keyboards import (
    get_main_menu_keyboard,
    get_tasks_keyboard,
    get_task_details_keyboard,
    get_balance_keyboard,
    get_profile_keyboard,
    get_responses_keyboard,
    get_settings_keyboard
)

logger = logging.getLogger(__name__)

router = Router()


async def handle_main_menu(callback: CallbackQuery):
    """
    Обработчик кнопки "Главное меню"
    """
    try:
        menu_text = """
🏠 <b>Главное меню</b>

Выберите действие:
"""
        from ui.menus import get_main_menu
        await callback.message.edit_text(
            menu_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в handle_main_menu: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def handle_auto_earn(callback: CallbackQuery):
    """
    Обработчик кнопки "Автоматический заработок"
    """
    try:
        text = """
⚙️ <b>Автоматический заработок</b>

Здесь вы можете настроить автоматическую работу бота:

📋 <b>Список заданий</b> - просмотр доступных заданий
✍️ <b>Мои отклики</b> - история ваших откликов
⚙️ <b>Настройки</b> - настройка автоматизации (скоро)

<i>В будущих версиях бот сможет работать полностью автономно!</i>
"""
        from ui.menus import get_auto_earn_menu
        await callback.message.edit_text(
            text,
            reply_markup=get_auto_earn_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в handle_auto_earn: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def handle_tasks_list(callback: CallbackQuery, task_service: TaskService):
    """
    Обработчик кнопки "Список заданий"
    """
    try:
        tasks = task_service.get_all_tasks()
        
        if not tasks:
            await callback.answer(
                "📭 Пока нет доступных заданий",
                show_alert=True
            )
            return
        
        tasks_text = f"""
📋 <b>Доступные задания ({len(tasks)})</b>

Выберите задание, чтобы увидеть детали и откликнуться:
"""
        
        await callback.message.edit_text(
            tasks_text,
            reply_markup=get_tasks_keyboard(tasks),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Пользователь {callback.from_user.id} открыл список заданий")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_tasks_list: {e}")
        await callback.answer("😔 Ошибка загрузки заданий", show_alert=True)


async def handle_task_details(callback: CallbackQuery, task_service: TaskService, user_service: UserService):
    """
    Обработчик кнопки "Подробнее о задании"
    """
    try:
        # Извлекаем task_id из callback_data
        task_id = int(callback.data.split("_")[-1])
        user_id = callback.from_user.id
        
        # Получаем задание
        task = task_service.get_task_by_id(task_id)
        if not task:
            await callback.answer(
                "❌ Задание не найдено",
                show_alert=True
            )
            return
        
        # Проверяем, откликался ли уже
        has_responded = await task_service.has_user_responded(user_id, task_id)
        
        task_text = f"""
📌 <b>{task['title']}</b>

📝 <b>Описание:</b>
{task['description']}

💰 <b>Бюджет:</b> {task['budget']}₽
🏷 <b>Категория:</b> {task['category']}

{'✅ <i>Вы уже откликнулись на это задание</i>' if has_responded else '💡 <i>Нажмите "Откликнуться" чтобы отправить отклик и получить +50₽</i>'}
"""
        
        await callback.message.edit_text(
            task_text,
            reply_markup=get_task_details_keyboard(task_id, has_responded),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Пользователь {user_id} просмотрел задание {task_id}")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_task_details: {e}")
        await callback.answer("😔 Ошибка загрузки задания", show_alert=True)


async def handle_task_respond(callback: CallbackQuery, task_service: TaskService, user_service: UserService):
    """
    Обработчик кнопки "Откликнуться"
    """
    try:
        # Извлекаем task_id из callback_data
        task_id = int(callback.data.split("_")[-1])
        user_id = callback.from_user.id
        
        # Проверяем задание
        task = task_service.get_task_by_id(task_id)
        if not task:
            await callback.answer(
                "❌ Задание не найдено",
                show_alert=True
            )
            return
        
        # Проверяем дубликат
        has_responded = await task_service.has_user_responded(user_id, task_id)
        if has_responded:
            await callback.answer(
                "⚠️ Вы уже откликались на это задание!",
                show_alert=True
            )
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
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("✅ Отклик отправлен!", show_alert=False)
        logger.info(f"Пользователь {user_id} откликнулся на задание {task_id}")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_task_respond: {e}")
        await callback.answer(
            f"😔 Ошибка: {str(e)}",
            show_alert=True
        )


async def handle_my_responses(callback: CallbackQuery, task_service: TaskService, user_service: UserService):
    """
    Обработчик кнопки "Мои отклики"
    """
    try:
        user_id = callback.from_user.id
        
        # Получаем отклики
        responses = await task_service.get_user_responses(user_id)
        
        if not responses:
            await callback.message.edit_text(
                "📭 У вас пока нет откликов.\n\n"
                "Используйте кнопку ниже, чтобы посмотреть доступные задания!",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Формируем текст с откликами (показываем последние 5)
        responses_text = f"📜 <b>История ваших откликов ({len(responses)}):</b>\n\n"
        
        for idx, resp in enumerate(responses[:5], 1):
            timestamp = resp.created_at.strftime("%d.%m.%Y %H:%M") if resp.created_at else "Неизвестно"
            responses_text += f"<b>{idx}. {resp.task_title}</b>\n"
            responses_text += f"📅 {timestamp}\n"
            responses_text += f"💬 <i>{resp.response_text[:80]}...</i>\n"
            responses_text += f"💰 Заработано: {resp.earned}₽\n"
            responses_text += "─" * 30 + "\n\n"
        
        user = await user_service.get_user_profile(user_id)
        responses_text += f"\n💳 <b>Общий баланс:</b> {user.balance}₽"
        
        if len(responses) > 5:
            responses_text += f"\n\n<i>Показаны последние 5 из {len(responses)} откликов</i>"
        
        await callback.message.edit_text(
            responses_text,
            reply_markup=get_responses_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Пользователь {user_id} просмотрел историю откликов")
        
    except Exception as e:
        logger.error(f"Ошибка в handle_my_responses: {e}")
        await callback.answer("😔 Ошибка загрузки откликов", show_alert=True)


async def handle_settings(callback: CallbackQuery):
    """
    Обработчик кнопки "Настройки" (заглушка)
    """
    try:
        settings_text = """
🔧 <b>Настройки</b>

<i>Функции настроек будут доступны в следующих версиях:</i>

🔔 Уведомления о новых заданиях
🌐 Выбор языка интерфейса
🎨 Персонализация откликов
⚙️ Дополнительные параметры

Следите за обновлениями! 🚀
"""
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=get_settings_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в handle_settings: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def handle_about(callback: CallbackQuery):
    """
    Обработчик кнопки "О боте"
    """
    try:
        about_text = """
ℹ️ <b>О боте</b>

<b>AI-Фриланс Ассистент v0.0.2</b>

Бот помогает автоматизировать работу на фриланс-биржах:
• Просмотр доступных заданий
• Автоматическая генерация откликов
• Отслеживание баланса и статистики

<b>Технологии:</b>
• Python 3.11
• aiogram 3.13.1
• Supabase (PostgreSQL)

<b>Разработчик:</b> @your_username

<b>Версия:</b> 0.0.2
<b>Дата релиза:</b> 14.11.2025

<i>Спасибо за использование бота! 💙</i>
"""
        
        await callback.message.edit_text(
            about_text,
            reply_markup=get_settings_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в handle_about: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def handle_already_responded(callback: CallbackQuery):
    """
    Обработчик кнопки "Вы уже откликнулись"
    """
    await callback.answer(
        "⚠️ Вы уже откликались на это задание!",
        show_alert=True
    )


async def handle_auto_settings_soon(callback: CallbackQuery):
    """Обработчик для настроек автозаработка (скоро)"""
    await callback.answer(
        "🔜 Настройки автоматизации будут доступны в версии 0.0.5!",
        show_alert=True
    )


def register_handlers(router: Router):
    """Регистрация всех callback обработчиков"""
    # Главное меню
    router.callback_query.register(handle_main_menu, lambda c: c.data == "main_menu")
    router.callback_query.register(handle_auto_earn, lambda c: c.data == "auto_earn")
    
    # Задания
    router.callback_query.register(handle_tasks_list, lambda c: c.data == "tasks_list")
    router.callback_query.register(handle_task_details, lambda c: c.data.startswith("task_details_"))
    router.callback_query.register(handle_task_respond, lambda c: c.data.startswith("task_respond_"))
    
    # Отклики
    router.callback_query.register(handle_my_responses, lambda c: c.data == "my_responses")
    
    # Настройки
    router.callback_query.register(handle_settings, lambda c: c.data == "settings")
    router.callback_query.register(handle_about, lambda c: c.data == "about")
    router.callback_query.register(handle_auto_settings_soon, lambda c: c.data == "auto_settings_soon")
    
    # Прочее
    router.callback_query.register(handle_already_responded, lambda c: c.data == "already_responded")
