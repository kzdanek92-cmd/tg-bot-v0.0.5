"""
Profile Handler
Обработчик команды /profile и просмотра профиля
"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from services.user_service import UserService
from keyboards.inline_keyboards import get_profile_keyboard, get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()


async def cmd_profile(message: Message, user_service: UserService):
    """
    Обработчик команды /profile
    
    Показывает профиль пользователя с статистикой
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
        
        # Получаем профиль и статистику
        user = await user_service.get_user_profile(user_id)
        stats = await user_service.get_user_stats(user_id)
        
        # Форматируем дату регистрации
        member_since = user.created_at.strftime("%d.%m.%Y") if user.created_at else "Неизвестно"
        
        # Определяем эмодзи для роли
        role_emoji = "⭐" if user.role == "pro" else "🆓"
        
        profile_text = f"""
🧾 <b>Ваш профиль</b>

👤 <b>Пользователь:</b> @{user.username}
🆔 <b>ID:</b> <code>{user.user_id}</code>
{role_emoji} <b>Статус:</b> {user.role.upper()}

💰 <b>Финансы:</b>
├ Текущий баланс: <b>{user.balance}₽</b>
├ Всего заработано: <b>{stats['total_earned']}₽</b>
└ Средний заработок: <b>{stats['avg_earned']:.2f}₽</b>

📊 <b>Статистика:</b>
├ Выполнено заданий: <b>{user.completed_tasks}</b>
├ Всего откликов: <b>{stats['total_responses']}</b>
└ Дата регистрации: <b>{member_since}</b>

<i>Продолжайте выполнять задания, чтобы увеличить свой баланс!</i>
"""
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} просмотрел свой профиль")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_profile для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Ошибка получения профиля. Попробуйте позже."
        )


async def show_profile(callback: CallbackQuery, user_service: UserService):
    """
    Обработчик callback для показа профиля через inline кнопку
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем профиль и статистику
        user = await user_service.get_user_profile(user_id)
        stats = await user_service.get_user_stats(user_id)
        
        if not user:
            await callback.answer(
                "⚠️ Профиль не найден. Используйте /start",
                show_alert=True
            )
            return
        
        # Форматируем дату регистрации
        member_since = user.created_at.strftime("%d.%m.%Y") if user.created_at else "Неизвестно"
        
        # Определяем эмодзи для роли
        role_emoji = "⭐" if user.role == "pro" else "🆓"
        
        profile_text = f"""
🧾 <b>Ваш профиль</b>

👤 <b>Пользователь:</b> @{user.username}
🆔 <b>ID:</b> <code>{user.user_id}</code>
{role_emoji} <b>Статус:</b> {user.role.upper()}

💰 <b>Финансы:</b>
├ Текущий баланс: <b>{user.balance}₽</b>
├ Всего заработано: <b>{stats['total_earned']}₽</b>
└ Средний заработок: <b>{stats['avg_earned']:.2f}₽</b>

📊 <b>Статистика:</b>
├ Выполнено заданий: <b>{user.completed_tasks}</b>
├ Всего откликов: <b>{stats['total_responses']}</b>
└ Дата регистрации: <b>{member_since}</b>

<i>Продолжайте выполнять задания, чтобы увеличить свой баланс!</i>
"""
        
        await callback.message.edit_text(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Пользователь {user_id} просмотрел профиль через callback")
        
    except Exception as e:
        logger.error(f"Ошибка в show_profile для пользователя {user_id}: {e}")
        await callback.answer(
            "😔 Ошибка получения профиля",
            show_alert=True
        )


def register_handlers(router: Router):
    """Регистрация обработчиков profile handler"""
    router.message.register(cmd_profile, Command("profile"))
    router.callback_query.register(show_profile, lambda c: c.data == "profile")
