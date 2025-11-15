"""
Error Handler
Глобальная обработка ошибок и декораторы
"""

import logging
from functools import wraps
from aiogram import Router
from aiogram.types import Update, ErrorEvent
from services.user_service import UserService

logger = logging.getLogger(__name__)

router = Router()


def require_registration(handler):
    """
    Декоратор для проверки регистрации пользователя
    
    Использование:
        @require_registration
        async def my_handler(message: Message, user_service: UserService):
            # Код выполнится только если пользователь зарегистрирован
            pass
    """
    @wraps(handler)
    async def wrapper(event, user_service: UserService, *args, **kwargs):
        # Получаем user_id из события
        if hasattr(event, 'from_user'):
            user_id = event.from_user.id
        else:
            logger.error("Не удалось получить user_id из события")
            return
        
        # Проверяем регистрацию
        is_registered = await user_service.is_user_registered(user_id)
        
        if not is_registered:
            # Отправляем сообщение о необходимости регистрации
            if hasattr(event, 'answer'):
                await event.answer(
                    "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
                )
            elif hasattr(event, 'message'):
                await event.message.answer(
                    "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
                )
            return
        
        # Пользователь зарегистрирован - выполняем handler
        return await handler(event, user_service, *args, **kwargs)
    
    return wrapper


async def global_error_handler(event: ErrorEvent):
    """
    Глобальный обработчик ошибок для бота
    
    Ловит все необработанные исключения и логирует их
    """
    update = event.update
    exception = event.exception
    
    # Логируем ошибку с контекстом
    logger.error(
        f"Необработанное исключение при обработке update {update.update_id}: {exception}",
        exc_info=True
    )
    
    # Пытаемся отправить сообщение пользователю
    try:
        if update.message:
            await update.message.answer(
                "😔 Произошла ошибка при обработке вашего запроса.\n"
                "Попробуйте позже или обратитесь в поддержку."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "😔 Произошла ошибка. Попробуйте позже.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке пользователю: {e}")


async def database_error_handler(update: Update, exception: Exception):
    """
    Обработчик ошибок базы данных
    
    Специфичная обработка для ошибок Supabase
    """
    logger.error(f"Ошибка базы данных: {exception}", exc_info=True)
    
    error_message = (
        "⚠️ Ошибка подключения к базе данных.\n"
        "Попробуйте позже или обратитесь в поддержку."
    )
    
    try:
        if update.message:
            await update.message.answer(error_message)
        elif update.callback_query:
            await update.callback_query.answer(
                "⚠️ Ошибка БД. Попробуйте позже.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке БД: {e}")


async def validation_error_handler(update: Update, exception: Exception):
    """
    Обработчик ошибок валидации
    
    Для ошибок валидации входных данных
    """
    logger.warning(f"Ошибка валидации: {exception}")
    
    error_message = (
        "❌ Некорректные данные.\n"
        f"Ошибка: {str(exception)}"
    )
    
    try:
        if update.message:
            await update.message.answer(error_message)
        elif update.callback_query:
            await update.callback_query.answer(
                f"❌ {str(exception)}",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке валидации: {e}")


def setup_error_handler(dp):
    """
    Настройка глобального обработчика ошибок
    
    Args:
        dp: Dispatcher aiogram
    """
    dp.error.register(global_error_handler)
    logger.info("Глобальный обработчик ошибок настроен")


class BotError(Exception):
    """Базовый класс для ошибок бота"""
    pass


class UserNotFoundError(BotError):
    """Пользователь не найден"""
    pass


class TaskNotFoundError(BotError):
    """Задание не найдено"""
    pass


class DuplicateResponseError(BotError):
    """Дублирование отклика"""
    pass


class InsufficientBalanceError(BotError):
    """Недостаточно средств"""
    pass


class DatabaseConnectionError(BotError):
    """Ошибка подключения к базе данных"""
    pass
