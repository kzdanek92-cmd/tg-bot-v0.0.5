"""
Task Service
Сервис для работы с заданиями и откликами
"""

import logging
from typing import List, Optional, Dict, Any
from database.supabase_client import SupabaseClient
from database.models import TaskResponse
from services.ai_service import AIService
from config import TASK_REWARD

logger = logging.getLogger(__name__)

# Тестовые задания (в памяти)
TASKS = [
    {
        "id": 1,
        "title": "Написать рекламный текст для кофейни",
        "description": "Нужен короткий рекламный текст (200-300 символов) для Instagram",
        "budget": 500,
        "category": "Копирайтинг"
    },
    {
        "id": 2,
        "title": "Придумать слоган для IT-стартапа",
        "description": "Стартап занимается разработкой мобильных приложений",
        "budget": 300,
        "category": "Креатив"
    },
    {
        "id": 3,
        "title": "Перевод текста с английского на русский",
        "description": "Технический текст, около 100 слов",
        "budget": 400,
        "category": "Переводы"
    },
    {
        "id": 4,
        "title": "Описание товара для маркетплейса",
        "description": "Написать SEO-оптимизированное описание для электроники",
        "budget": 350,
        "category": "Копирайтинг"
    },
    {
        "id": 5,
        "title": "Создать пост для LinkedIn",
        "description": "Пост о важности soft skills в IT",
        "budget": 250,
        "category": "SMM"
    }
]


class TaskService:
    """
    Сервис для управления заданиями и откликами
    
    Предоставляет бизнес-логику для получения заданий,
    создания откликов и работы с историей
    """
    
    def __init__(self, db_client: SupabaseClient, ai_service: AIService):
        """
        Инициализация сервиса
        
        Args:
            db_client: Клиент для работы с Supabase
            ai_service: Сервис для AI-генерации откликов
        """
        self.db = db_client
        self.ai = ai_service
        logger.info("TaskService инициализирован")
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Получить список всех доступных заданий
        
        Returns:
            Список заданий
        """
        logger.debug(f"Получен список из {len(TASKS)} заданий")
        return TASKS
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить задание по ID
        
        Args:
            task_id: ID задания
            
        Returns:
            Словарь с данными задания или None если не найдено
        """
        task = next((t for t in TASKS if t["id"] == task_id), None)
        
        if task:
            logger.debug(f"Задание {task_id} найдено")
        else:
            logger.debug(f"Задание {task_id} не найдено")
        
        return task
    
    async def has_user_responded(self, user_id: int, task_id: int) -> bool:
        """
        Проверить, откликался ли пользователь на задание
        
        Args:
            user_id: Telegram user ID
            task_id: ID задания
            
        Returns:
            True если отклик существует, False иначе
        """
        try:
            exists = await self.db.check_response_exists(user_id, task_id)
            logger.debug(f"Проверка отклика пользователя {user_id} на задание {task_id}: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Ошибка проверки существования отклика: {e}")
            raise
    
    async def create_response(self, user_id: int, task_id: int) -> TaskResponse:
        """
        Создать отклик на задание
        
        Генерирует AI-отклик, сохраняет в БД, обновляет баланс и счетчик заданий
        
        Args:
            user_id: Telegram user ID
            task_id: ID задания
            
        Returns:
            Созданный объект TaskResponse
            
        Raises:
            Exception: Если задание не найдено, отклик уже существует или ошибка БД
        """
        try:
            # Проверяем существование задания
            task = self.get_task_by_id(task_id)
            if not task:
                raise Exception(f"Задание {task_id} не найдено")
            
            # Проверяем, не откликался ли уже
            if await self.has_user_responded(user_id, task_id):
                raise Exception(f"Вы уже откликались на задание {task_id}")
            
            # Генерируем AI-отклик
            response_text = self.ai.generate_response(task)
            logger.info(f"AI-отклик сгенерирован для пользователя {user_id} на задание {task_id}")
            
            # Создаем объект отклика
            response = TaskResponse(
                user_id=user_id,
                task_id=task_id,
                task_title=task["title"],
                response_text=response_text,
                earned=TASK_REWARD
            )
            
            # Сохраняем в БД
            created_response = await self.db.create_response(response)
            
            # Обновляем баланс пользователя
            await self.db.update_balance(user_id, TASK_REWARD)
            
            # Увеличиваем счетчик выполненных заданий
            await self.db.increment_completed_tasks(user_id)
            
            logger.info(f"Отклик пользователя {user_id} на задание {task_id} успешно создан")
            
            return created_response
            
        except Exception as e:
            logger.error(f"Ошибка создания отклика: {e}")
            raise
    
    async def get_user_responses(self, user_id: int) -> List[TaskResponse]:
        """
        Получить все отклики пользователя
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Список объектов TaskResponse
        """
        try:
            responses = await self.db.get_user_responses(user_id)
            logger.debug(f"Получено {len(responses)} откликов пользователя {user_id}")
            return responses
            
        except Exception as e:
            logger.error(f"Ошибка получения откликов пользователя {user_id}: {e}")
            raise
    
    async def get_response_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получить статистику откликов пользователя
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Словарь со статистикой
        """
        try:
            responses = await self.get_user_responses(user_id)
            
            if not responses:
                return {
                    "total_responses": 0,
                    "total_earned": 0,
                    "avg_earned": 0,
                    "categories": {}
                }
            
            # Подсчет по категориям
            categories = {}
            for response in responses:
                task = self.get_task_by_id(response.task_id)
                if task:
                    category = task["category"]
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += 1
            
            return {
                "total_responses": len(responses),
                "total_earned": sum(r.earned for r in responses),
                "avg_earned": sum(r.earned for r in responses) / len(responses),
                "categories": categories,
                "latest_response": responses[0].created_at if responses else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики откликов пользователя {user_id}: {e}")
            raise
    
    def get_tasks_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Получить задания по категории
        
        Args:
            category: Название категории
            
        Returns:
            Список заданий в категории
        """
        tasks = [t for t in TASKS if t["category"] == category]
        logger.debug(f"Найдено {len(tasks)} заданий в категории {category}")
        return tasks
    
    def get_available_categories(self) -> List[str]:
        """
        Получить список доступных категорий
        
        Returns:
            Список уникальных категорий
        """
        categories = list(set(t["category"] for t in TASKS))
        logger.debug(f"Доступные категории: {categories}")
        return categories
