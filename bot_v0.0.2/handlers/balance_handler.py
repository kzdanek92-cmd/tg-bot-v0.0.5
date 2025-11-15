"""
Balance Handler
Обработчик команды /balance и просмотра баланса
"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from services.user_service import UserService
from services.task_service import TaskService
from keyboards.inline_keyboards import get_balance_keyboard

logger = logging.getLogger(__name__)

router = Router()


async def cmd_balance(message: Message, user_service: UserService, task_service: TaskService):
    """
    Обработчик команды /balance
    
    Показывает текущий баланс и статистику пользователя
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
        
        # Получаем данные пользователя и статистику
        user = await user_service.get_user_profile(user_id)
        stats = await task_service.get_response_stats(user_id)
        
        # Определяем прогресс до следующего уровня (пример)
        next_level_balance = ((user.balance // 500) + 1) * 500
        progress = (user.balance % 500) / 500 * 100
        
        balance_text = f"""
💳 <b>Ваш баланс</b>

💰 <b>Текущий баланс:</b> <b>{user.balance}₽</b>
📊 <b>Откликов отправлено:</b> {user.completed_tasks}
💵 <b>Всего заработано:</b> {stats['total_earned']}₽
📈 <b>Средний заработок:</b> {stats['avg_earned']:.2f}₽

<b>Прогресс:</b>
{'█' * int(progress // 10)}{'░' * (10 - int(progress // 10))} {progress:.0f}%
<i>До {next_level_balance}₽ осталось {next_level_balance - user.balance}₽</i>

<i>Отправляйте отклики на задания, чтобы увеличить баланс!</i>
"""
        
        await message.answer(
            balance_text,
            reply_markup=get_balance_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} проверил баланс")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_balance для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Ошибка получения баланса. Попробуйте позже."
        )


async def show_balance(callback: CallbackQuery, user_service: UserService, task_service: TaskService):
    """
    Обработчик callback для показа баланса через inline кнопку
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем данные пользователя и статистику
        user = await user_service.get_user_profile(user_id)
        stats = await task_service.get_response_stats(user_id)
        
        if not user:
            await callback.answer(
                "⚠️ Профиль не найден. Используйте /start",
                show_alert=True
            )
            return
        
        # Определяем прогресс до следующего уровня
        next_level_balance = ((user.balance // 500) + 1) * 500
        progress = (user.balance % 500) / 500 * 100
        
        balance_text = f"""
💳 <b>Ваш баланс</b>

💰 <b>Текущий баланс:</b> <b>{user.balance}₽</b>
📊 <b>Откликов отправлено:</b> {user.completed_tasks}
💵 <b>Всего заработано:</b> {stats['total_earned']}₽
📈 <b>Средний заработок:</b> {stats['avg_earned']:.2f}₽

<b>Прогресс:</b>
{'█' * int(progress // 10)}{'░' * (10 - int(progress // 10))} {progress:.0f}%
<i>До {next_level_balance}₽ осталось {next_level_balance - user.balance}₽</i>

<i>Отправляйте отклики на задания, чтобы увеличить баланс!</i>
"""
        
        await callback.message.edit_text(
            balance_text,
            reply_markup=get_balance_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Пользователь {user_id} проверил баланс через callback")
        
    except Exception as e:
        logger.error(f"Ошибка в show_balance для пользователя {user_id}: {e}")
        await callback.answer(
            "😔 Ошибка получения баланса",
            show_alert=True
        )


def register_handlers(router: Router):
    """Регистрация обработчиков balance handler"""
    router.message.register(cmd_balance, Command("balance"))
    router.callback_query.register(show_balance, lambda c: c.data == "balance")
