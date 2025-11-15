# 🏗️ Архитектура проекта

## Текущая версия (0.1)

### Структура кода:

```
bot.py
├── Конфигурация
│   ├── BOT_TOKEN
│   ├── USER_DATA_FILE
│   └── TASKS (тестовые данные)
│
├── Работа с данными
│   ├── load_user_data()
│   ├── save_user_data()
│   ├── get_user()
│   └── update_user()
│
├── AI-генерация
│   └── generate_response()
│
└── Обработчики команд
    ├── /start
    ├── /help
    ├── /tasks
    ├── /respond
    ├── /balance
    └── /my_responses
```

### Хранение данных:

**user_data.json:**
```json
{
  "123456789": {
    "balance": 150,
    "responses": [
      {
        "task_id": 1,
        "task_title": "Написать рекламный текст",
        "response_text": "Здравствуйте! Готов выполнить...",
        "timestamp": "2025-11-14T15:30:00",
        "earned": 50
      }
    ],
    "created_at": "2025-11-14T15:00:00"
  }
}
```

---

## Планируемая архитектура (0.2+)

### Модульная структура:

```
project/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Точка входа
│   ├── config.py            # Конфигурация
│   └── handlers/            # Обработчики команд
│       ├── __init__.py
│       ├── start.py
│       ├── tasks.py
│       ├── responses.py
│       └── balance.py
│
├── database/
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy модели
│   ├── crud.py              # CRUD операции
│   └── migrations/          # Alembic миграции
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py        # AI-генерация
│   ├── freelance_api.py     # API бирж
│   └── payment_service.py   # Платежи
│
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
│
├── tests/
│   ├── test_handlers.py
│   ├── test_services.py
│   └── test_database.py
│
├── requirements.txt
├── .env                     # Переменные окружения
└── README.md
```

### База данных (PostgreSQL):

```sql
-- Таблица пользователей
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    balance DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица откликов
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    task_id INTEGER,
    task_title VARCHAR(500),
    response_text TEXT,
    earned DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица заданий (кэш с бирж)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255),
    platform VARCHAR(50),
    title VARCHAR(500),
    description TEXT,
    budget DECIMAL(10, 2),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица транзакций
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    amount DECIMAL(10, 2),
    type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API интеграции:

```python
# services/freelance_api.py

class FreelanceAPI:
    """Базовый класс для работы с API бирж"""
    
    async def get_tasks(self, filters):
        """Получить список заданий"""
        pass
    
    async def send_response(self, task_id, text):
        """Отправить отклик"""
        pass

class FLruAPI(FreelanceAPI):
    """API для FL.ru"""
    pass

class KworkAPI(FreelanceAPI):
    """API для Kwork"""
    pass
```

### AI-сервис:

```python
# services/ai_service.py

class AIService:
    """Сервис для генерации откликов"""
    
    def __init__(self, provider='openai'):
        self.provider = provider
    
    async def generate_response(self, task, user_profile):
        """
        Генерирует персонализированный отклик
        
        Args:
            task: Данные задания
            user_profile: Профиль пользователя (навыки, опыт)
        
        Returns:
            str: Сгенерированный отклик
        """
        if self.provider == 'openai':
            return await self._generate_openai(task, user_profile)
        elif self.provider == 'yandex':
            return await self._generate_yandex(task, user_profile)
```

---

## Масштабирование

### Версия 0.3: Микросервисы

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ Bot   │ │ Web   │
│Service│ │Service│
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────────┐
    │   Message   │
    │   Queue     │
    │  (RabbitMQ) │
    └────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│  AI   │ │ Task  │
│Service│ │Scraper│
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │Database │
    │(Postgres│
    │ + Redis)│
    └─────────┘
```

### Производительность:

- **Кэширование:** Redis для частых запросов
- **Очереди:** RabbitMQ для асинхронной обработки
- **Балансировка:** Nginx для распределения нагрузки
- **Мониторинг:** Prometheus + Grafana

---

## Безопасность

### Текущая версия (0.1):
- ✅ Базовая валидация входных данных
- ✅ Хранение данных локально

### Планы (0.2+):
- 🔒 Шифрование токенов API
- 🔒 Rate limiting (защита от спама)
- 🔒 JWT авторизация для веб-интерфейса
- 🔒 HTTPS для всех соединений
- 🔒 Логирование всех операций
- 🔒 Регулярные бэкапы БД

---

## Тестирование

### Текущее:
- Ручное тестирование команд

### Планируемое:
```python
# tests/test_handlers.py

import pytest
from bot.handlers import start, tasks, respond

@pytest.mark.asyncio
async def test_start_command():
    """Тест команды /start"""
    message = MockMessage(text="/start")
    await start.cmd_start(message)
    assert "Добро пожаловать" in message.answer_text

@pytest.mark.asyncio
async def test_respond_command():
    """Тест команды /respond"""
    message = MockMessage(text="/respond 1")
    await respond.cmd_respond(message)
    assert message.user_balance == 50
```

---

## Мониторинг и логирование

```python
import logging
from prometheus_client import Counter, Histogram

# Метрики
responses_total = Counter('responses_total', 'Total responses sent')
response_time = Histogram('response_time', 'Response generation time')

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

---

## Развертывание

### Текущее (0.1):
```bash
python bot.py
```

### Планируемое (0.2+):

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: freelance_bot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
  
  redis:
    image: redis:7-alpine
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: freelance-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: freelance-bot
  template:
    metadata:
      labels:
        app: freelance-bot
    spec:
      containers:
      - name: bot
        image: freelance-bot:latest
        env:
        - name: BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: bot-secrets
              key: token
```
