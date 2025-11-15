"""
Data Models
Модели данных для пользователей и откликов
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    """
    Модель пользователя
    
    Attributes:
        user_id: Telegram user ID
        username: Telegram username
        balance: Баланс пользователя в рублях
        completed_tasks: Количество выполненных заданий
        role: Роль пользователя (free/pro)
        created_at: Дата регистрации
    """
    user_id: int
    username: str
    balance: float = 0.0
    completed_tasks: int = 0
    role: str = "free"
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Валидация полей после инициализации"""
        # Валидация user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError(f"user_id должен быть положительным числом, получено: {self.user_id}")
        
        # Валидация username
        if not self.username or not isinstance(self.username, str):
            raise ValueError(f"username должен быть непустой строкой, получено: {self.username}")
        
        # Валидация balance
        if not isinstance(self.balance, (int, float)) or self.balance < 0:
            raise ValueError(f"balance должен быть неотрицательным числом, получено: {self.balance}")
        
        # Валидация completed_tasks
        if not isinstance(self.completed_tasks, int) or self.completed_tasks < 0:
            raise ValueError(f"completed_tasks должен быть неотрицательным целым числом, получено: {self.completed_tasks}")
        
        # Валидация role
        valid_roles = ["free", "pro"]
        if self.role not in valid_roles:
            raise ValueError(f"role должен быть одним из {valid_roles}, получено: {self.role}")
        
        # Установка created_at если не задано
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертация объекта в словарь для Supabase
        
        Returns:
            Dict с полями для вставки в БД
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "balance": float(self.balance),
            "completed_tasks": self.completed_tasks,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Создание объекта User из словаря (из Supabase)
        
        Args:
            data: Словарь с данными из БД
            
        Returns:
            Объект User
        """
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            balance=float(data.get('balance', 0.0)),
            completed_tasks=int(data.get('completed_tasks', 0)),
            role=data.get('role', 'free'),
            created_at=created_at
        )
    
    def __repr__(self) -> str:
        """Строковое представление объекта"""
        return (f"User(user_id={self.user_id}, username='{self.username}', "
                f"balance={self.balance}, completed_tasks={self.completed_tasks}, "
                f"role='{self.role}')")


@dataclass
class TaskResponse:
    """
    Модель отклика на задание
    
    Attributes:
        user_id: Telegram user ID
        task_id: ID задания
        task_title: Название задания
        response_text: Текст отклика
        earned: Заработано рублей за отклик
        created_at: Дата создания отклика
    """
    user_id: int
    task_id: int
    task_title: str
    response_text: str
    earned: float
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Валидация полей после инициализации"""
        # Валидация user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError(f"user_id должен быть положительным числом, получено: {self.user_id}")
        
        # Валидация task_id
        if not isinstance(self.task_id, int) or self.task_id <= 0:
            raise ValueError(f"task_id должен быть положительным числом, получено: {self.task_id}")
        
        # Валидация task_title
        if not self.task_title or not isinstance(self.task_title, str):
            raise ValueError(f"task_title должен быть непустой строкой, получено: {self.task_title}")
        
        # Валидация response_text
        if not self.response_text or not isinstance(self.response_text, str):
            raise ValueError(f"response_text должен быть непустой строкой, получено: {self.response_text}")
        
        # Валидация earned
        if not isinstance(self.earned, (int, float)) or self.earned < 0:
            raise ValueError(f"earned должен быть неотрицательным числом, получено: {self.earned}")
        
        # Установка created_at если не задано
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертация объекта в словарь для Supabase
        
        Returns:
            Dict с полями для вставки в БД
        """
        return {
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "response_text": self.response_text,
            "earned": float(self.earned),
            "created_at": self.created_at.isoformat() if self.created_at else datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResponse':
        """
        Создание объекта TaskResponse из словаря (из Supabase)
        
        Args:
            data: Словарь с данными из БД
            
        Returns:
            Объект TaskResponse
        """
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        return cls(
            user_id=data['user_id'],
            task_id=data['task_id'],
            task_title=data['task_title'],
            response_text=data['response_text'],
            earned=float(data['earned']),
            created_at=created_at
        )
    
    def __repr__(self) -> str:
        """Строковое представление объекта"""
        return (f"TaskResponse(user_id={self.user_id}, task_id={self.task_id}, "
                f"task_title='{self.task_title}', earned={self.earned})")


@dataclass
class Payment:
    """
    Модель платежа

    Attributes:
        user_id: Telegram user ID
        currency: Валюта платежа (TON, USDT, BTC, FK etc.)
        amount: Сумма (в единицах валюты, например TON или USDT)
        tx_id: Хеш транзакции или идентификатор счета/invoice
        status: Статус платежа (pending, paid, failed)
        meta: Дополнительные данные (dict)
        created_at: Время создания
    """
    user_id: int
    currency: str
    amount: float
    tx_id: Optional[str] = None
    status: str = "pending"
    meta: Optional[Dict[str, Any]] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "currency": self.currency,
            "amount": float(self.amount),
            "tx_id": self.tx_id,
            "status": self.status,
            "meta": self.meta,
            "created_at": self.created_at.isoformat() if self.created_at else datetime.now().isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return cls(
            user_id=int(data['user_id']),
            currency=data.get('currency', ''),
            amount=float(data.get('amount', 0.0)),
            tx_id=data.get('tx_id'),
            status=data.get('status', 'pending'),
            meta=data.get('meta', {}),
            created_at=created_at
        )
