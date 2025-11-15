"""
Start Handler
Обработчик команды /start и регистрации пользователей
"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from services.user_service import UserService
from keyboards.inline_keyboards import get_registration_keyboard
from ui.menus import get_main_menu

logger = logging.getLogger(__name__)

router = Router()


async def cmd_start(message: Message, user_service: UserService):
    """
    Обработчик команды /start
    
    Проверяет регистрацию пользователя:
    - Если не зарегистрирован - предлагает регистрацию
    - Если зарегистрирован - показывает главное меню
    """
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    try:
        # Проверяем регистрацию
        is_registered = await user_service.is_user_registered(user_id)
        
        if not is_registered:
            # Пользователь не зарегистрирован - показываем приветствие и кнопку регистрации
            welcome_text = f"""
👋 <b>Привет, {username}!</b>

Добро пожаловать в <b>AI-Фриланс Ассистент</b>!

Я помогу тебе автоматизировать работу на фриланс-биржах:
• 📋 Просматривать доступные задания
• ✍️ Автоматически генерировать отклики
• 💰 Зарабатывать виртуальные рубли
• 📊 Отслеживать свой прогресс

<b>Для начала работы нужно зарегистрироваться:</b>
"""
            await message.answer(
                welcome_text,
                reply_markup=get_registration_keyboard(),
                parse_mode="HTML"
            )
            logger.info(f"Новый пользователь {user_id} ({username}) открыл бота")
        else:
            # Пользователь уже зарегистрирован - показываем главное меню
            user = await user_service.get_user_profile(user_id)
            
            welcome_back_text = f"""
👋 <b>С возвращением, {user.username}!</b>

💰 Ваш баланс: <b>{user.balance}₽</b>
📊 Выполнено заданий: <b>{user.completed_tasks}</b>
🏷 Статус: <b>{user.role.upper()}</b>

Выберите действие:
"""
            await message.answer(
                welcome_back_text,
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            logger.info(f"Пользователь {user_id} ({username}) вернулся в бота")
            
    except Exception as e:
        logger.error(f"Ошибка в cmd_start для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при запуске бота. Попробуйте позже или обратитесь в поддержку."
        )


async def process_registration(callback: CallbackQuery, user_service: UserService):
    """
    Обработчик регистрации через inline кнопку
    
    Создает пользователя в БД и показывает приветственное сообщение
    """
    user_id = callback.from_user.id
    username = callback.from_user.username or f"user_{user_id}"
    
    try:
        # Регистрируем пользователя
        user = await user_service.register_user(user_id, username)
        
        # Отправляем приветственное сообщение
        success_text = f"""
✅ <b>Регистрация успешна!</b>

Добро пожаловать, <b>{user.username}</b>!

🎁 Ваш стартовый баланс: <b>{user.balance}₽</b>
🏷 Статус: <b>{user.role.upper()}</b>

<b>Как это работает:</b>
1. Выберите "📋 Список заданий"
2. Найдите интересное задание
3. Нажмите "Откликнуться"
4. Получите +50₽ на баланс

Удачи! 🚀
"""
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Вы успешно зарегистрированы!")
        logger.info(f"Пользователь {user_id} ({username}) успешно зарегистрирован")
        
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя {user_id}: {e}")
        await callback.answer(
            "😔 Ошибка регистрации. Попробуйте позже.",
            show_alert=True
        )


def register_handlers(router: Router):
    """Регистрация обработчиков start handler"""
    router.message.register(cmd_start, Command("start"))
    router.callback_query.register(process_registration, lambda c: c.data == "register")
