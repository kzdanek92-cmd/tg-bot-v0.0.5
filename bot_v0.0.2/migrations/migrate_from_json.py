"""
Migration Script
Миграция данных из user_data.json (v0.0.1) в Supabase (v0.0.2)
"""

import json
import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import SupabaseClient
from database.models import User, TaskResponse
import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# КОНФИГУРАЦИЯ МИГРАЦИИ
# ============================================================================

# Путь к JSON файлу из версии 0.0.1
JSON_FILE_PATH = "../user_data.json"  # Относительно bot_v0.0.2/


async def load_json_data(file_path: str) -> dict:
    """
    Загрузка данных из JSON файла
    
    Args:
        file_path: Путь к JSON файлу
        
    Returns:
        Словарь с данными пользователей
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не найден")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Загружено данных из {file_path}: {len(data)} пользователей")
        return data
        
    except Exception as e:
        logger.error(f"Ошибка загрузки JSON: {e}")
        return {}


async def migrate_users(db_client: SupabaseClient, json_data: dict) -> tuple:
    """
    Миграция пользователей из JSON в Supabase
    
    Args:
        db_client: Клиент Supabase
        json_data: Данные из JSON
        
    Returns:
        Tuple (успешно, ошибок)
    """
    success_count = 0
    error_count = 0
    
    logger.info("Начало миграции пользователей...")
    
    for user_id_str, user_data in json_data.items():
        try:
            user_id = int(user_id_str)
            
            # Проверяем, не существует ли уже пользователь
            existing_user = await db_client.get_user(user_id)
            if existing_user:
                logger.warning(f"Пользователь {user_id} уже существует, пропускаем")
                continue
            
            # Создаем объект User
            user = User(
                user_id=user_id,
                username=user_data.get('username', f'user_{user_id}'),
                balance=float(user_data.get('balance', 0)),
                completed_tasks=len(user_data.get('responses', [])),
                role='free',
                created_at=datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat()))
            )
            
            # Сохраняем в Supabase
            await db_client.create_user(user)
            success_count += 1
            logger.info(f"✅ Пользователь {user_id} мигрирован")
            
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Ошибка миграции пользователя {user_id_str}: {e}")
    
    logger.info(f"Миграция пользователей завершена: {success_count} успешно, {error_count} ошибок")
    return success_count, error_count


async def migrate_responses(db_client: SupabaseClient, json_data: dict) -> tuple:
    """
    Миграция откликов из JSON в Supabase
    
    Args:
        db_client: Клиент Supabase
        json_data: Данные из JSON
        
    Returns:
        Tuple (успешно, ошибок)
    """
    success_count = 0
    error_count = 0
    
    logger.info("Начало миграции откликов...")
    
    for user_id_str, user_data in json_data.items():
        try:
            user_id = int(user_id_str)
            responses = user_data.get('responses', [])
            
            for response_data in responses:
                try:
                    # Проверяем, не существует ли уже отклик
                    task_id = response_data.get('task_id')
                    exists = await db_client.check_response_exists(user_id, task_id)
                    if exists:
                        logger.warning(f"Отклик пользователя {user_id} на задание {task_id} уже существует, пропускаем")
                        continue
                    
                    # Создаем объект TaskResponse
                    response = TaskResponse(
                        user_id=user_id,
                        task_id=task_id,
                        task_title=response_data.get('task_title', 'Неизвестное задание'),
                        response_text=response_data.get('response_text', ''),
                        earned=float(response_data.get('earned', 50)),
                        created_at=datetime.fromisoformat(response_data.get('timestamp', datetime.now().isoformat()))
                    )
                    
                    # Сохраняем в Supabase
                    await db_client.create_response(response)
                    success_count += 1
                    logger.info(f"✅ Отклик пользователя {user_id} на задание {task_id} мигрирован")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Ошибка миграции отклика: {e}")
            
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Ошибка обработки откликов пользователя {user_id_str}: {e}")
    
    logger.info(f"Миграция откликов завершена: {success_count} успешно, {error_count} ошибок")
    return success_count, error_count


async def verify_migration(db_client: SupabaseClient, json_data: dict):
    """
    Проверка корректности миграции
    
    Args:
        db_client: Клиент Supabase
        json_data: Исходные данные из JSON
    """
    logger.info("Проверка миграции...")
    
    json_users_count = len(json_data)
    json_responses_count = sum(len(user_data.get('responses', [])) for user_data in json_data.values())
    
    logger.info(f"В JSON было: {json_users_count} пользователей, {json_responses_count} откликов")
    
    # Проверяем несколько пользователей
    verified_users = 0
    for user_id_str in list(json_data.keys())[:5]:  # Проверяем первых 5
        try:
            user_id = int(user_id_str)
            user = await db_client.get_user(user_id)
            if user:
                verified_users += 1
                logger.info(f"✅ Пользователь {user_id} найден в Supabase")
        except Exception as e:
            logger.error(f"❌ Ошибка проверки пользователя {user_id_str}: {e}")
    
    logger.info(f"Проверено пользователей: {verified_users}/5")


async def main():
    """Главная функция миграции"""
    logger.info("=" * 70)
    logger.info("🔄 МИГРАЦИЯ ДАННЫХ ИЗ v0.0.1 В v0.0.2")
    logger.info("=" * 70)
    
    try:
        # Инициализация Supabase клиента
        logger.info("Подключение к Supabase...")
        db_client = SupabaseClient(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        # Проверка подключения
        health = await db_client.health_check()
        if not health:
            logger.error("❌ Не удалось подключиться к Supabase")
            return
        
        logger.info("✅ Подключение к Supabase успешно")
        
        # Загрузка данных из JSON
        json_data = await load_json_data(JSON_FILE_PATH)
        
        if not json_data:
            logger.warning("⚠️ Нет данных для миграции")
            return
        
        # Подтверждение миграции
        print("\n" + "=" * 70)
        print(f"Найдено пользователей для миграции: {len(json_data)}")
        total_responses = sum(len(user_data.get('responses', [])) for user_data in json_data.values())
        print(f"Найдено откликов для миграции: {total_responses}")
        print("=" * 70)
        
        confirm = input("\nПродолжить миграцию? (yes/no): ")
        if confirm.lower() not in ['yes', 'y', 'да']:
            logger.info("Миграция отменена пользователем")
            return
        
        # Миграция пользователей
        users_success, users_errors = await migrate_users(db_client, json_data)
        
        # Миграция откликов
        responses_success, responses_errors = await migrate_responses(db_client, json_data)
        
        # Проверка миграции
        await verify_migration(db_client, json_data)
        
        # Итоговая статистика
        logger.info("=" * 70)
        logger.info("📊 ИТОГОВАЯ СТАТИСТИКА МИГРАЦИИ")
        logger.info("=" * 70)
        logger.info(f"Пользователи: {users_success} успешно, {users_errors} ошибок")
        logger.info(f"Отклики: {responses_success} успешно, {responses_errors} ошибок")
        logger.info("=" * 70)
        
        if users_errors == 0 and responses_errors == 0:
            logger.info("✅ Миграция завершена успешно!")
        else:
            logger.warning("⚠️ Миграция завершена с ошибками. Проверьте логи.")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка миграции: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
