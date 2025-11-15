"""
AI-Фриланс Ассистент - Telegram Bot
Версия: 0.0.2
Описание: Бот для автоматизации откликов на фриланс-биржах с Supabase интеграцией
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Импорт конфигурации
import config

# Импорт database layer
from database.supabase_client import SupabaseClient

# Импорт services
from services.user_service import UserService
from services.task_service import TaskService
from services.ai_service import AIService

# Импорт handlers
from handlers import start_handler, profile_handler, tasks_handler, balance_handler, callback_handler
from handlers import payments_handler, info_handler

# Импорт payments
from payments.crypto import CryptoPaymentService
from payments.freekassa import FreeKassaService

# Импорт utils
from utils.error_handler import setup_error_handler

# ============================================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================================

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ
# ============================================================================

# Инициализация бота
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Инициализация dispatcher
dp = Dispatcher()

# Инициализация database client
db_client = SupabaseClient(config.SUPABASE_URL, config.SUPABASE_KEY)

# Инициализация services
user_service = UserService(db_client)
ai_service = AIService()
task_service = TaskService(db_client, ai_service)

# Инициализация payment service
crypto_service = None
if config.CRYPTOBOT_TOKEN:
    crypto_service = CryptoPaymentService(config.CRYPTOBOT_TOKEN)
    logger.info("CryptoBot payment service инициализирован")
else:
    logger.warning("CryptoBot payment service не инициализирован (отсутствует токен)")

# FreeKassa
freekassa_service = None
if getattr(config, 'FREEKASSA_MERCHANT_ID', None) and getattr(config, 'FREEKASSA_SECRET1', None) and getattr(config, 'FREEKASSA_SECRET2', None):
    freekassa_service = FreeKassaService(
        merchant_id=config.FREEKASSA_MERCHANT_ID,
        secret1=config.FREEKASSA_SECRET1,
        secret2=config.FREEKASSA_SECRET2
    )
    logger.info("FreeKassa service initialized")
else:
    logger.info("FreeKassa service not configured")

# ============================================================================
# MIDDLEWARE ДЛЯ ПЕРЕДАЧИ СЕРВИСОВ В HANDLERS
# ============================================================================

@dp.message.middleware()
async def inject_services_message(handler, event, data):
    """Middleware для передачи сервисов в message handlers"""
    data['user_service'] = user_service
    data['task_service'] = task_service
    data['ai_service'] = ai_service
    return await handler(event, data)


@dp.callback_query.middleware()
async def inject_services_callback(handler, event, data):
    """Middleware для передачи сервисов в callback handlers"""
    data['user_service'] = user_service
    data['task_service'] = task_service
    data['ai_service'] = ai_service
    data['crypto_service'] = crypto_service
    data['freekassa_service'] = freekassa_service
    return await handler(event, data)

# ============================================================================
# РЕГИСТРАЦИЯ HANDLERS
# ============================================================================

# Регистрируем handlers из модулей
start_handler.register_handlers(dp)
profile_handler.register_handlers(dp)
tasks_handler.register_handlers(dp)
balance_handler.register_handlers(dp)
callback_handler.register_handlers(dp)
payments_handler.register_handlers(dp)
info_handler.register_handlers(dp)

# Настройка глобального обработчика ошибок
setup_error_handler(dp)

# ============================================================================
# КОМАНДЫ БОТА
# ============================================================================

async def set_bot_commands():
    """Установка команд бота для меню"""
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="tasks", description="📋 Список заданий"),
        BotCommand(command="profile", description="🧾 Мой профиль"),
        BotCommand(command="balance", description="💰 Проверить баланс"),
        BotCommand(command="my_responses", description="✍️ Мои отклики"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")

# ============================================================================
# ЗАПУСК И ОСТАНОВКА БОТА
# ============================================================================

async def on_startup():
    """Действия при запуске бота"""
    logger.info("=" * 50)
    logger.info("🤖 AI-Фриланс Ассистент v0.0.2 запускается...")
    logger.info("=" * 50)
    
    # Проверка подключения к Supabase
    try:
        health = await db_client.health_check()
        if health:
            logger.info("✅ Подключение к Supabase успешно")
        else:
            logger.error("❌ Ошибка подключения к Supabase")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка подключения к Supabase: {e}")
        raise
    
    # Установка команд бота
    await set_bot_commands()
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username}")
    logger.info(f"ID бота: {bot_info.id}")
    logger.info("=" * 50)
    logger.info("✅ Бот готов к работе!")
    logger.info("Нажмите Ctrl+C для остановки")
    logger.info("=" * 50)
    # Запустим лёгкий aiohttp сервер для приёма callback'ов платежных провайдеров
    try:
        from aiohttp import web

        app = web.Application()

        async def cryptobot_webhook(request):
            try:
                data = await request.json()
            except Exception:
                data = await request.post()

            # Валидация webhook
            if not crypto_service:
                return web.Response(text='Crypto service not configured', status=400)

            valid = await crypto_service.verify_webhook(data)
            if not valid:
                return web.Response(text='Invalid webhook', status=400)

            # Попытаемся извлечь invoice id и статус
            inv = None
            status = None
            try:
                inv = data.get('payload') or data.get('invoice_id') or (data.get('result') or {}).get('invoice_id')
                status = (data.get('update_type') or data.get('status') or (data.get('result') or {}).get('status'))
            except Exception:
                pass

            if inv:
                try:
                    # Обновляем запись в Supabase
                    await db_client.update_payment_status(tx_id=str(inv), updates={"status": status or 'paid'})

                    # Если статус paid — начисляем пользователю баланс
                    if status == 'paid':
                        rec = await db_client.get_payment_by_tx(str(inv))
                        if rec:
                            uid = rec.get('user_id')
                            amt = float(rec.get('amount', 0))
                            # Для TON — переводим в рубли по курсу 50₽
                            if rec.get('currency') == 'TON':
                                await user_service.update_balance(uid, amt * 50)
                            elif rec.get('currency') in ('USDT', 'BTC'):
                                # тут можно добавить конвертацию по курсу или начислять в валюте — пока начисляем в рублях по умолчанию 0
                                await user_service.update_balance(uid, 0)
                except Exception as e:
                    logger.error(f"Ошибка обработки cryptobot webhook: {e}")

            return web.Response(text='ok')

        async def freekassa_callback(request):
            post = await request.post()
            data = {k: post.get(k) for k in post.keys()}

            if not freekassa_service:
                return web.Response(text='FreeKassa not configured', status=400)

            valid = freekassa_service.verify_notification(data)
            if not valid:
                return web.Response(text='Invalid', status=400)

            order_id = data.get('MERCHANT_ORDER_ID') or data.get('o') or data.get('MERCHANT_ORDER_ID')
            amount = float(data.get('AMOUNT') or data.get('oa') or 0)

            try:
                # Обновим платёж и зачислим сумму
                rec = await db_client.get_payment_by_tx(order_id)
                if rec:
                    await db_client.update_payment_status(tx_id=order_id, updates={"status": "paid"})
                    uid = rec.get('user_id')
                    # Зачисляем рубли
                    await user_service.update_balance(uid, amount)
            except Exception as e:
                logger.error(f"Ошибка обработки FreeKassa callback: {e}")

            return web.Response(text='OK')

        app.router.add_post('/webhook/cryptobot', cryptobot_webhook)
        app.router.add_post('/webhook/freekassa', freekassa_callback)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info('Callback HTTP server started on 0.0.0.0:8080')
    except Exception as e:
        logger.warning(f'Не удалось запустить callback server: {e}')


async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("=" * 50)
    logger.info("🛑 Остановка бота...")
    logger.info("=" * 50)
    
    # Закрытие соединений
    await bot.session.close()
    
    logger.info("✅ Бот остановлен")
    logger.info("=" * 50)

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

async def main():
    """Главная функция запуска бота"""
    try:
        # Действия при запуске
        await on_startup()
        
        # Удаляем старые обновления и запускаем polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        # Действия при остановке
        await on_shutdown()


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}", exc_info=True)
