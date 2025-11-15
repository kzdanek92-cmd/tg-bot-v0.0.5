# Design Document - Telegram Bot Version 0.0.2

## Overview

Версия 0.0.2 представляет собой архитектурное улучшение бота с переходом от файлового хранилища JSON к облачной базе данных Supabase. Дизайн фокусируется на модульности, расширяемости и улучшенном пользовательском опыте через inline-клавиатуры.

### Ключевые изменения от v0.0.1:
- Замена JSON-хранилища на Supabase PostgreSQL
- Добавление системы регистрации и профилей
- Внедрение inline-клавиатур для навигации
- Улучшенная обработка ошибок
- Модульная архитектура кода

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram User                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Telegram Bot API                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Bot Application                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Handlers Layer                         │  │
│  │  - Command Handlers (/start, /profile, etc.)    │  │
│  │  - Callback Query Handlers (inline buttons)     │  │
│  │  - Error Handlers                                │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│  ┌──────────────▼───────────────────────────────────┐  │
│  │           Business Logic Layer                   │  │
│  │  - User Service (registration, profile)         │  │
│  │  - Task Service (tasks, responses)              │  │
│  │  - Balance Service (balance operations)         │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│  ┌──────────────▼───────────────────────────────────┐  │
│  │           Database Layer                         │  │
│  │  - Supabase Client                               │  │
│  │  - Database Operations (CRUD)                    │  │
│  └──────────────┬───────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Supabase (PostgreSQL)                       │
│  - users table                                           │
│  - responses table                                       │
└─────────────────────────────────────────────────────────┘
```

### Module Structure

```
bot_v0.0.2/
├── bot.py                      # Точка входа, инициализация
├── config.py                   # Конфигурация (токены, URL)
├── database/
│   ├── __init__.py
│   ├── supabase_client.py     # Supabase клиент
│   └── models.py              # Модели данных
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py       # /start, регистрация
│   ├── profile_handler.py     # /profile
│   ├── tasks_handler.py       # /tasks, отклики
│   ├── balance_handler.py     # /balance
│   └── callback_handler.py    # Inline кнопки
├── services/
│   ├── __init__.py
│   ├── user_service.py        # Логика пользователей
│   ├── task_service.py        # Логика заданий
│   └── ai_service.py          # AI-генерация откликов
├── keyboards/
│   ├── __init__.py
│   └── inline_keyboards.py    # Inline клавиатуры
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Валидация данных
│   └── error_handler.py       # Обработка ошибок
├── migrations/
│   └── migrate_from_json.py   # Миграция из v0.0.1
├── requirements.txt
└── README.md
```

## Components and Interfaces

### 1. Database Layer

#### Supabase Client (`database/supabase_client.py`)

```python
class SupabaseClient:
    """Клиент для работы с Supabase"""
    
    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        
    async def create_user(self, user_data: Dict) -> Dict:
        """Создать нового пользователя"""
        
    async def update_user(self, user_id: int, updates: Dict) -> Dict:
        """Обновить данные пользователя"""
        
    async def get_user_responses(self, user_id: int) -> List[Dict]:
        """Получить все отклики пользователя"""
        
    async def create_response(self, response_data: Dict) -> Dict:
        """Создать новый отклик"""
        
    async def check_response_exists(self, user_id: int, task_id: int) -> bool:
        """Проверить существование отклика"""
```

#### Data Models (`database/models.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    username: str
    balance: float = 0.0
    completed_tasks: int = 0
    role: str = "free"
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Конвертация в словарь для Supabase"""
        
@dataclass
class TaskResponse:
    user_id: int
    task_id: int
    task_title: str
    response_text: str
    earned: float
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Конвертация в словарь для Supabase"""
```

### 2. Service Layer

#### User Service (`services/user_service.py`)

```python
class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
    
    async def register_user(self, user_id: int, username: str) -> User:
        """Регистрация нового пользователя"""
        
    async def get_user_profile(self, user_id: int) -> Optional[User]:
        """Получить профиль пользователя"""
        
    async def is_user_registered(self, user_id: int) -> bool:
        """Проверить регистрацию пользователя"""
        
    async def update_balance(self, user_id: int, amount: float) -> User:
        """Обновить баланс пользователя"""
        
    async def increment_completed_tasks(self, user_id: int) -> User:
        """Увеличить счетчик выполненных заданий"""
```

#### Task Service (`services/task_service.py`)

```python
class TaskService:
    """Сервис для работы с заданиями"""
    
    def __init__(self, db_client: SupabaseClient, ai_service: AIService):
        self.db = db_client
        self.ai = ai_service
    
    async def get_all_tasks(self) -> List[Dict]:
        """Получить все доступные задания"""
        
    async def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Получить задание по ID"""
        
    async def create_response(self, user_id: int, task_id: int) -> TaskResponse:
        """Создать отклик на задание"""
        
    async def get_user_responses(self, user_id: int) -> List[TaskResponse]:
        """Получить все отклики пользователя"""
        
    async def has_user_responded(self, user_id: int, task_id: int) -> bool:
        """Проверить наличие отклика пользователя"""
```

### 3. Handler Layer

#### Start Handler (`handlers/start_handler.py`)

```python
async def cmd_start(message: Message, user_service: UserService):
    """
    Обработчик команды /start
    - Проверяет регистрацию пользователя
    - Если не зарегистрирован - предлагает регистрацию
    - Если зарегистрирован - показывает главное меню
    """
    
async def process_registration(callback: CallbackQuery, user_service: UserService):
    """
    Обработчик регистрации через inline кнопку
    - Создает пользователя в БД
    - Показывает приветственное сообщение
    """
```

#### Callback Handler (`handlers/callback_handler.py`)

```python
async def handle_main_menu(callback: CallbackQuery):
    """Обработчик кнопок главного меню"""
    
async def handle_tasks_list(callback: CallbackQuery, task_service: TaskService):
    """Обработчик кнопки "Список заданий" """
    
async def handle_task_details(callback: CallbackQuery, task_service: TaskService):
    """Обработчик кнопки "Подробнее о задании" """
    
async def handle_task_respond(callback: CallbackQuery, task_service: TaskService, user_service: UserService):
    """Обработчик кнопки "Откликнуться" """
    
async def handle_balance(callback: CallbackQuery, user_service: UserService):
    """Обработчик кнопки "Баланс" """
    
async def handle_profile(callback: CallbackQuery, user_service: UserService):
    """Обработчик кнопки "Профиль" """
```

### 4. Keyboard Layer

#### Inline Keyboards (`keyboards/inline_keyboards.py`)

```python
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список заданий", callback_data="tasks_list")],
        [InlineKeyboardButton(text="✍️ Мои отклики", callback_data="my_responses")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🧾 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🔧 Настройки", callback_data="settings")]
    ])

def get_tasks_keyboard(tasks: List[Dict]) -> InlineKeyboardMarkup:
    """Клавиатура со списком заданий"""
    
def get_task_details_keyboard(task_id: int, has_responded: bool) -> InlineKeyboardMarkup:
    """Клавиатура для деталей задания"""
    
def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка "Назад" """
```

## Data Models

### Database Schema

#### Users Table

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    balance NUMERIC(10, 2) DEFAULT 0.00,
    completed_tasks INTEGER DEFAULT 0,
    role TEXT DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_user_id ON users(user_id);
```

#### Responses Table

```sql
CREATE TABLE responses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id INTEGER NOT NULL,
    task_title TEXT NOT NULL,
    response_text TEXT NOT NULL,
    earned NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_responses_user_id ON responses(user_id);
CREATE INDEX idx_responses_task_id ON responses(task_id);
CREATE UNIQUE INDEX idx_responses_user_task ON responses(user_id, task_id);
```

### Data Flow

#### Registration Flow

```
User sends /start
    ↓
Check if user exists in DB
    ↓
    ├─ Yes → Show main menu
    │
    └─ No → Show registration prompt
            ↓
        User clicks "Зарегистрироваться"
            ↓
        Create user in Supabase
            ↓
        Show welcome message + main menu
```

#### Task Response Flow

```
User clicks "Список заданий"
    ↓
Fetch tasks from memory (static data)
    ↓
Display tasks with inline buttons
    ↓
User clicks "Подробнее" on task
    ↓
Check if user already responded
    ↓
Display task details + "Откликнуться" button
    ↓
User clicks "Откликнуться"
    ↓
Generate AI response
    ↓
Save response to Supabase
    ↓
Update user balance (+50₽)
    ↓
Increment completed_tasks
    ↓
Show success message
```

## Error Handling

### Error Types and Handling Strategy

#### 1. Database Connection Errors

```python
try:
    result = await db.get_user(user_id)
except Exception as e:
    logger.error(f"Database error: {e}")
    await message.answer(
        "⚠️ Ошибка подключения к базе данных. Попробуйте позже.",
        reply_markup=get_main_menu_keyboard()
    )
```

#### 2. User Not Registered Errors

```python
async def require_registration(handler):
    """Декоратор для проверки регистрации"""
    async def wrapper(message: Message, user_service: UserService):
        if not await user_service.is_user_registered(message.from_user.id):
            await message.answer(
                "⚠️ Вы не зарегистрированы. Используйте /start для регистрации."
            )
            return
        return await handler(message, user_service)
    return wrapper
```

#### 3. Duplicate Response Errors

```python
if await task_service.has_user_responded(user_id, task_id):
    await callback.answer(
        "⚠️ Вы уже откликались на это задание!",
        show_alert=True
    )
    return
```

#### 4. Invalid Task ID Errors

```python
task = await task_service.get_task_by_id(task_id)
if not task:
    await callback.answer(
        "❌ Задание не найдено!",
        show_alert=True
    )
    return
```

### Global Error Handler

```python
@dp.error()
async def error_handler(update: Update, exception: Exception):
    """Глобальный обработчик ошибок"""
    logger.error(f"Update {update} caused error {exception}")
    
    if update.message:
        await update.message.answer(
            "😔 Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        )
    elif update.callback_query:
        await update.callback_query.answer(
            "😔 Произошла ошибка. Попробуйте позже.",
            show_alert=True
        )
```

## Testing Strategy

### Unit Tests

```python
# tests/test_user_service.py
async def test_register_user():
    """Тест регистрации пользователя"""
    
async def test_get_user_profile():
    """Тест получения профиля"""
    
async def test_update_balance():
    """Тест обновления баланса"""

# tests/test_task_service.py
async def test_create_response():
    """Тест создания отклика"""
    
async def test_duplicate_response():
    """Тест дублирования отклика"""
```

### Integration Tests

```python
# tests/test_integration.py
async def test_full_registration_flow():
    """Тест полного флоу регистрации"""
    
async def test_task_response_flow():
    """Тест полного флоу отклика на задание"""
```

### Manual Testing Checklist

1. ✅ Регистрация нового пользователя
2. ✅ Повторный /start для зарегистрированного пользователя
3. ✅ Просмотр списка заданий через inline кнопки
4. ✅ Отклик на задание через inline кнопки
5. ✅ Проверка баланса после отклика
6. ✅ Просмотр профиля
7. ✅ Просмотр истории откликов
8. ✅ Попытка повторного отклика на задание
9. ✅ Обратная совместимость с текстовыми командами
10. ✅ Обработка ошибок БД

## Configuration

### Environment Variables

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Settings
TASK_REWARD = 50  # Рублей за отклик
DEFAULT_ROLE = "free"
```

### .env File Template

```
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

## Migration Strategy

### Migration Script (`migrations/migrate_from_json.py`)

```python
async def migrate_from_json_to_supabase():
    """
    Миграция данных из user_data.json в Supabase
    
    1. Читает user_data.json
    2. Для каждого пользователя:
       - Создает запись в users table
       - Создает записи в responses table
    3. Выводит статистику миграции
    """
    
    # Загрузить JSON
    with open('user_data.json', 'r') as f:
        data = json.load(f)
    
    # Мигрировать пользователей
    for user_id, user_data in data.items():
        await db.create_user({
            'user_id': int(user_id),
            'username': user_data.get('username', 'unknown'),
            'balance': user_data['balance'],
            'completed_tasks': len(user_data['responses']),
            'role': 'free',
            'created_at': user_data['created_at']
        })
        
        # Мигрировать отклики
        for response in user_data['responses']:
            await db.create_response({
                'user_id': int(user_id),
                'task_id': response['task_id'],
                'task_title': response['task_title'],
                'response_text': response['response_text'],
                'earned': response['earned'],
                'created_at': response['timestamp']
            })
```

## Performance Considerations

### Database Optimization

1. **Индексы**: Созданы индексы на user_id и task_id для быстрого поиска
2. **Connection Pooling**: Supabase автоматически управляет пулом соединений
3. **Кэширование**: Статические данные (список заданий) хранятся в памяти

### Response Time Goals

- Регистрация пользователя: < 1 секунда
- Получение профиля: < 500ms
- Создание отклика: < 1 секунда
- Отображение списка заданий: < 300ms

## Security Considerations

1. **API Keys**: Хранятся в .env файле, не коммитятся в Git
2. **SQL Injection**: Supabase SDK автоматически защищает от SQL-инъекций
3. **User Input Validation**: Валидация всех входных данных
4. **Rate Limiting**: Будет добавлено в версии 0.0.3
5. **Error Messages**: Не раскрывают внутреннюю структуру системы

## Future Enhancements (v0.0.3+)

1. Реальная AI-генерация через OpenAI/YandexGPT
2. Интеграция с API фриланс-бирж
3. Система подписок (Free/Pro)
4. Платежная система
5. Веб-интерфейс для управления
6. Аналитика и статистика
7. Уведомления о новых заданиях
8. Персонализация откликов
