"""
Supabase Client
Клиент для работы с базой данных Supabase
"""

import logging
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from .models import User, TaskResponse

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Клиент для работы с Supabase PostgreSQL
    
    Предоставляет методы для работы с пользователями и откликами
    """
    
    def __init__(self, url: str, key: str):
        """
        Инициализация клиента Supabase
        
        Args:
            url: URL проекта Supabase
            key: API ключ Supabase
        """
        try:
            self.client: Client = create_client(url, key)
            logger.info("Supabase клиент успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Supabase клиента: {e}")
            raise
    
    # ========================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
    # ========================================================================
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Объект User или None если не найден
        """
        try:
            response = self.client.table('users').select('*').eq('user_id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                return User.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            raise
    
    async def create_user(self, user: User) -> User:
        """
        Создать нового пользователя
        
        Args:
            user: Объект User для создания
            
        Returns:
            Созданный объект User
        """
        try:
            data = user.to_dict()
            response = self.client.table('users').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Пользователь {user.user_id} успешно создан")
                return User.from_dict(response.data[0])
            
            raise Exception("Не удалось создать пользователя")
            
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {user.user_id}: {e}")
            raise
    
    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> User:
        """
        Обновить данные пользователя
        
        Args:
            user_id: Telegram user ID
            updates: Словарь с полями для обновления
            
        Returns:
            Обновленный объект User
        """
        try:
            response = self.client.table('users').update(updates).eq('user_id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Пользователь {user_id} успешно обновлен")
                return User.from_dict(response.data[0])
            
            raise Exception(f"Пользователь {user_id} не найден")
            
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
            raise
    
    async def update_balance(self, user_id: int, amount: float) -> User:
        """
        Обновить баланс пользователя (добавить сумму)
        
        Args:
            user_id: Telegram user ID
            amount: Сумма для добавления к балансу
            
        Returns:
            Обновленный объект User
        """
        try:
            # Получаем текущий баланс
            user = await self.get_user(user_id)
            if not user:
                raise Exception(f"Пользователь {user_id} не найден")
            
            # Обновляем баланс
            new_balance = user.balance + amount
            return await self.update_user(user_id, {"balance": new_balance})
            
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
        """
        try:
            # Получаем текущее значение
            user = await self.get_user(user_id)
            if not user:
                raise Exception(f"Пользователь {user_id} не найден")
            
            # Увеличиваем счетчик
            new_count = user.completed_tasks + 1
            return await self.update_user(user_id, {"completed_tasks": new_count})
            
        except Exception as e:
            logger.error(f"Ошибка увеличения счетчика заданий пользователя {user_id}: {e}")
            raise
    
    # ========================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ОТКЛИКАМИ
    # ========================================================================
    
    async def get_user_responses(self, user_id: int) -> List[TaskResponse]:
        """
        Получить все отклики пользователя
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Список объектов TaskResponse
        """
        try:
            response = self.client.table('responses').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            
            if response.data:
                return [TaskResponse.from_dict(item) for item in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения откликов пользователя {user_id}: {e}")
            raise
    
    async def create_response(self, response: TaskResponse) -> TaskResponse:
        """
        Создать новый отклик
        
        Args:
            response: Объект TaskResponse для создания
            
        Returns:
            Созданный объект TaskResponse
        """
        try:
            data = response.to_dict()
            result = self.client.table('responses').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Отклик пользователя {response.user_id} на задание {response.task_id} создан")
                return TaskResponse.from_dict(result.data[0])
            
            raise Exception("Не удалось создать отклик")
            
        except Exception as e:
            logger.error(f"Ошибка создания отклика: {e}")
            raise
    
    async def check_response_exists(self, user_id: int, task_id: int) -> bool:
        """
        Проверить существование отклика пользователя на задание
        
        Args:
            user_id: Telegram user ID
            task_id: ID задания
            
        Returns:
            True если отклик существует, False иначе
        """
        try:
            response = self.client.table('responses').select('id').eq('user_id', user_id).eq('task_id', task_id).execute()
            
            return response.data and len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Ошибка проверки существования отклика: {e}")
            raise
    
    async def get_response_by_id(self, response_id: int) -> Optional[TaskResponse]:
        """
        Получить отклик по ID
        
        Args:
            response_id: ID отклика
            
        Returns:
            Объект TaskResponse или None если не найден
        """
        try:
            response = self.client.table('responses').select('*').eq('id', response_id).execute()
            
            if response.data and len(response.data) > 0:
                return TaskResponse.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения отклика {response_id}: {e}")
            raise
    
    # ========================================================================
    # УТИЛИТЫ
    # ========================================================================
    
    async def health_check(self) -> bool:
        """
        Проверка подключения к Supabase
        
        Returns:
            True если подключение работает, False иначе
        """
        try:
            # Пробуем выполнить простой запрос
            self.client.table('users').select('id').limit(1).execute()
            logger.info("Supabase health check: OK")
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

    # ========================================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПЛАТЕЖАМИ
    # ========================================================================

    async def create_payment(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать запись о платеже в таблице `payments`

        Args:
            payment: Словарь с полями платежа

        Returns:
            Вставленная запись
        """
        try:
            result = self.client.table('payments').insert(payment).execute()
            if result.data and len(result.data) > 0:
                logger.info(f"Платеж создан: {result.data[0]}")
                return result.data[0]
            raise Exception("Не удалось создать запись платежа")
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            raise

    async def update_payment_status(self, tx_id: str = None, invoice_id: str = None, updates: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Обновить запись платежа по tx_id или invoice_id
        """
        try:
            if not updates:
                updates = {}

            query = self.client.table('payments')
            if tx_id:
                query = query.update(updates).eq('tx_id', tx_id)
            elif invoice_id:
                query = query.update(updates).eq('tx_id', invoice_id)
            else:
                raise ValueError('tx_id или invoice_id должны быть переданы')

            result = query.execute()
            if result.data and len(result.data) > 0:
                logger.info(f"Платеж обновлён: {result.data[0]}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления платежа: {e}")
            raise

    async def get_payment_by_tx(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить запись платежа по tx_id (или invoice id)
        """
        try:
            result = self.client.table('payments').select('*').eq('tx_id', tx_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Ошибка получения платежа по tx {tx_id}: {e}")
            raise

    async def get_payments_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить все платежи пользователя
        """
        try:
            result = self.client.table('payments').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            if result.data:
                return result.data
            return []
        except Exception as e:
            logger.error(f"Ошибка получения платежей пользователя {user_id}: {e}")
            raise
