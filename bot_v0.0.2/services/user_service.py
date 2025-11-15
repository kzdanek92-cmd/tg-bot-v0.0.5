"""
User Service
Сервис для работы с пользователями
"""

import logging
from typing import Optional
from database.supabase_client import SupabaseClient
from database.models import User

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для управления пользователями
    
    Предоставляет бизнес-логику для регистрации, получения профиля,
    обновления баланса и других операций с пользователями
    """
    
    def __init__(self, db_client: SupabaseClient):
        """
        Инициализация сервиса
        
        Args:
            db_client: Клиент для работы с Supabase
        """
        self.db = db_client
        logger.info("UserService инициализирован")
    
    async def register_user(self, user_id: int, username: str) -> User:
        """
        Регистрация нового пользователя
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            
        Returns:
            Созданный объект User
            
        Raises:
            Exception: Если пользователь уже существует или ошибка БД
        """
        try:
            # Проверяем, не зарегистрирован ли уже
            existing_user = await self.db.get_user(user_id)
            if existing_user:
                logger.warning(f"Попытка повторной регистрации пользователя {user_id}")
                raise Exception(f"Пользователь {user_id} уже зарегистрирован")
            
            # Создаем нового пользователя
            new_user = User(
                user_id=user_id,
                username=username,
                balance=0.0,
                completed_tasks=0,
                role="free"
            )
            
            created_user = await self.db.create_user(new_user)
            logger.info(f"Пользователь {user_id} ({username}) успешно зарегистрирован")
            
            return created_user
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя {user_id}: {e}")
            raise
    
    async def get_user_profile(self, user_id: int) -> Optional[User]:
        """
        Получить профиль пользователя
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Объект User или None если не найден
        """
        try:
            user = await self.db.get_user(user_id)
            
            if user:
                logger.debug(f"Профиль пользователя {user_id} получен")
            else:
                logger.debug(f"Пользователь {user_id} не найден")
            
            return user
            
        except Exception as e:
            logger.error(f"Ошибка получения профиля пользователя {user_id}: {e}")
            raise
    
    async def is_user_registered(self, user_id: int) -> bool:
        """
        Проверить, зарегистрирован ли пользователь
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True если зарегистрирован, False иначе
        """
        try:
            user = await self.db.get_user(user_id)
            return user is not None
            
        except Exception as e:
            logger.error(f"Ошибка проверки регистрации пользователя {user_id}: {e}")
            # В случае ошибки БД считаем что не зарегистрирован
            return False
    
    async def update_balance(self, user_id: int, amount: float) -> User:
        """
        Обновить баланс пользователя (добавить сумму)
        
        Args:
            user_id: Telegram user ID
            amount: Сумма для добавления (может быть отрицательной)
            
        Returns:
            Обновленный объект User
            
        Raises:
            Exception: Если пользователь не найден или ошибка БД
        """
        try:
            # Проверяем существование пользователя
            user = await self.db.get_user(user_id)
            if not user:
                raise Exception(f"Пользователь {user_id} не найден")
            
            # Проверяем, что баланс не станет отрицательным
            new_balance = user.balance + amount
            if new_balance < 0:
                raise Exception(f"Недостаточно средств. Текущий баланс: {user.balance}, попытка списать: {abs(amount)}")
            
            # Обновляем баланс
            updated_user = await self.db.update_balance(user_id, amount)
            logger.info(f"Баланс пользователя {user_id} обновлен: {user.balance} -> {updated_user.balance}")
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Ошибка обновления баланса пользователя {user_id}: {e}")
            raise
    
    async def increment_completed_tasks(self, user_id: int) -> User:
        """
        Увеличить счетчик выполненных заданий на 1
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Обновленный объект User
            
        Raises:
            Exception: Если пользователь не найден или ошибка БД
        """
        try:
            # Проверяем существование пользователя
            user = await self.db.get_user(user_id)
            if not user:
                raise Exception(f"Пользователь {user_id} не найден")
            
            # Увеличиваем счетчик
            updated_user = await self.db.increment_completed_tasks(user_id)
            logger.info(f"Счетчик заданий пользователя {user_id} увеличен: {user.completed_tasks} -> {updated_user.completed_tasks}")
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Ошибка увеличения счетчика заданий пользователя {user_id}: {e}")
            raise
    
    async def update_username(self, user_id: int, new_username: str) -> User:
        """
        Обновить username пользователя
        
        Args:
            user_id: Telegram user ID
            new_username: Новый username
            
        Returns:
            Обновленный объект User
        """
        try:
            updated_user = await self.db.update_user(user_id, {"username": new_username})
            logger.info(f"Username пользователя {user_id} обновлен на {new_username}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Ошибка обновления username пользователя {user_id}: {e}")
            raise
    
    async def upgrade_to_pro(self, user_id: int) -> User:
        """
        Повысить пользователя до Pro роли
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Обновленный объект User
        """
        try:
            updated_user = await self.db.update_user(user_id, {"role": "pro"})
            logger.info(f"Пользователь {user_id} повышен до Pro")
            return updated_user
            
        except Exception as e:
            logger.error(f"Ошибка повышения пользователя {user_id} до Pro: {e}")
            raise
    
    async def get_user_stats(self, user_id: int) -> dict:
        """
        Получить статистику пользователя
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Словарь со статистикой
        """
        try:
            user = await self.db.get_user(user_id)
            if not user:
                raise Exception(f"Пользователь {user_id} не найден")
            
            responses = await self.db.get_user_responses(user_id)
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "balance": user.balance,
                "completed_tasks": user.completed_tasks,
                "role": user.role,
                "total_responses": len(responses),
                "total_earned": sum(r.earned for r in responses),
                "avg_earned": sum(r.earned for r in responses) / len(responses) if responses else 0,
                "member_since": user.created_at
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики пользователя {user_id}: {e}")
            raise
