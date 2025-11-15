"""
Configuration Module
Управление переменными окружения и настройками приложения
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# ============================================================================
# TELEGRAM BOT CONFIGURATION
# ============================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте .env файл.")

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL не найден в переменных окружения. Проверьте .env файл.")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY не найден в переменных окружения. Проверьте .env файл.")

# ============================================================================
# CRYPTOBOT CONFIGURATION
# ============================================================================

CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

# Награда за выполнение задания (в рублях)
TASK_REWARD = 50

# Роль пользователя по умолчанию
DEFAULT_ROLE = "free"

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

import logging
logger = logging.getLogger(__name__)

# Проверим CRYPTOBOT_TOKEN после инициализации логгера
if not CRYPTOBOT_TOKEN:
    logger.warning("CRYPTOBOT_TOKEN не найден. Платежи через CryptoBot будут недоступны.")

# ============================================================================
# FREEKASSA CONFIGURATION
# ============================================================================

FREEKASSA_MERCHANT_ID = os.getenv("FREEKASSA_MERCHANT_ID")
FREEKASSA_SECRET1 = os.getenv("FREEKASSA_SECRET1")
FREEKASSA_SECRET2 = os.getenv("FREEKASSA_SECRET2")

if not (FREEKASSA_MERCHANT_ID and FREEKASSA_SECRET1 and FREEKASSA_SECRET2):
    logger.info("FreeKassa keys not fully set. FreeKassa payments will be unavailable.")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """
    Валидация конфигурации при запуске приложения
    Проверяет наличие всех необходимых переменных
    """
    required_vars = {
        "BOT_TOKEN": BOT_TOKEN,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}\n"
            f"Создайте .env файл на основе .env.example"
        )
    
    return True


# Валидация при импорте модуля
validate_config()
