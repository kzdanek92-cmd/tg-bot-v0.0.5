PROJECT_STRUCTURE.md — Структура проекта v0.0.5
================================================================================

КОРНЕВАЯ ПАПКА: bot_v0.0.2/
├── bot.py                              [Главный файл бота + HTTP сервер]
├── config.py                           [Конфигурация и переменные окружения]
├── requirements.txt                    [Зависимости Python]
├── .env.example                        [Пример .env файла]
│
├── VERSION_0.0.5_SUMMARY.md            [Этот файл]
├── UPGRADE_TO_v0.0.5.md                [Руководство миграции]
├── TESTING_GUIDE_v0.0.5.md             [Руководство тестирования]
│
│
├── database/                           [Модули базы данных]
│   ├── __init__.py
│   ├── models.py                       [Модели: User, TaskResponse, Payment]
│   ├── supabase_client.py              [Клиент Supabase + методы платежей]
│   ├── schema.sql                      [Базовая схема БД]
│   └── migrations/
│       └── 001_create_payments_table.sql [Миграция для таблицы payments]
│
├── payments/                           [Модули обработки платежей]
│   ├── __init__.py
│   ├── crypto.py                       [CryptoBot API (TON, USDT, BTC)]
│   └── freekassa.py                    [FreeKassa API (генерация ссылок + callback)]
│
├── services/                           [Бизнес-логика]
│   ├── __init__.py
│   ├── user_service.py                 [Сервис управления пользователями]
│   ├── ai_service.py                   [AI сервис]
│   ├── task_service.py                 [Сервис заданий]
│   └── exchange_service.py             [Сервис курсов валют (CoinGecko)]
│
├── handlers/                           [Обработчики Telegram событий]
│   ├── __init__.py
│   ├── start_handler.py                [Обработчик /start]
│   ├── profile_handler.py              [Профиль пользователя]
│   ├── balance_handler.py              [Проверка баланса]
│   ├── tasks_handler.py                [Список заданий]
│   ├── callback_handler.py             [Обработка callback'ов меню]
│   ├── payments_handler.py             [Обработка платежей (TON/USDT/BTC/FreeKassa)]
│   └── info_handler.py                 [Информационные разделы]
│
├── ui/                                 [Интерфейс]
│   ├── __init__.py
│   └── menus.py                        [Все меню и клавиатуры]
│
├── utils/                              [Утилиты]
│   ├── __init__.py
│   └── error_handler.py                [Обработка ошибок]
│
├── docs/                               [Документация]
│   ├── CHANGELOG_v0.0.0.4.md          [Changelog для v0.0.4]
│   └── CHANGELOG_v0.0.0.5.md          [Changelog для v0.0.5]
│
├── __pycache__/                        [Кеш Python (игнорировать)]
│
└── test_webhooks.py                    [Скрипт для тестирования webhook'ов]


================================================================================
ПОДРОБНОЕ ОПИСАНИЕ ФАЙЛОВ
================================================================================

🟢 ОСНОВНЫЕ ФАЙЛЫ (ГЛАВНЫЕ)
═══════════════════════════════════════════════════════════════════════════

📄 bot.py
─────────
Главный файл бота. Содержит:
  • Инициализация Bot и Dispatcher
  • Инициализация всех сервисов (DB, CryptoBot, FreeKassa)
  • Middleware для injection сервисов в handlers
  • Регистрация всех handlers
  • Запуск HTTP сервера для webhook'ов (порт 8080)
  • Обработчики webhook'ов (CryptoBot и FreeKassa)
  • Функции startup/shutdown

Ключевые функции:
  - on_startup() — инициализация при запуске
  - on_shutdown() — очистка при остановке
  - cryptobot_webhook() — обработка callback от CryptoBot
  - freekassa_callback() — обработка callback от FreeKassa

📄 config.py
────────────
Конфигурация приложения. Содержит:
  • Загрузка .env переменных через python-dotenv
  • BOT_TOKEN — токен Telegram бота
  • SUPABASE_URL, SUPABASE_KEY — Supabase credentials
  • CRYPTOBOT_TOKEN — токен CryptoBot API
  • FREEKASSA_* — ключи FreeKassa
  • Логирование и валидация конфигурации

Используется во всех модулях для получения переменных окружения


🟢 МОДУЛИ ПЛАТЕЖЕЙ
═══════════════════════════════════════════════════════════════════════════

📄 payments/crypto.py
─────────────────────
Сервис для работы с CryptoBot API.
  • Создание инвойсов (invoices) для всех валют
  • Проверка статуса платежа
  • Получение курсов обмена
  • Получение баланса аккаунта
  • Верификация webhook'ов

Методы:
  - create_invoice() → создать счет (TON/USDT/BTC)
  - get_invoice() → получить информацию о счете
  - check_invoice_status() → проверить статус
  - get_balance() → баланс аккаунта
  - get_exchange_rates() → курсы валют
  - get_payment_url() → ссылка для оплаты
  - verify_webhook() → проверка webhook

📄 payments/freekassa.py
────────────────────────
Сервис для работы с FreeKassa API (НОВЫЙ).
  • Генерация ссылок на оплату с подписью MD5
  • Верификация callback уведомлений
  • Проверка подписи (secret1/secret2)

Методы:
  - generate_payment_link() → ссылка на FreeKassa
  - verify_notification() → проверка webhook подписи

📄 services/exchange_service.py
───────────────────────────────
Сервис курсов валют (НОВЫЙ).
  • Получение текущих курсов через CoinGecko API
  • Кеширование курсов
  • Fallback на предустановленные курсы
  • Конвертация в рубли

Методы:
  - get_rate() → получить курс валюты
  - convert_to_rub() → конвертировать в рубли
  - set_cache() → установить курс в кеш
  - get_cache() → получить весь кеш


🟢 БАЗА ДАННЫХ
═══════════════════════════════════════════════════════════════════════════

📄 database/models.py
──────────────────────
Модели данных.
  • User — пользователь Telegram
  • TaskResponse — отклик на задание
  • Payment — транзакция платежа (НОВОЕ)

Каждая модель имеет:
  - to_dict() → сериализация для БД
  - from_dict() → десериализация из БД
  - Валидация полей

📄 database/supabase_client.py
──────────────────────────────
Клиент для работы с Supabase.

Методы пользователей:
  - get_user() / create_user() / update_user()
  - update_balance() / increment_completed_tasks()

Методы откликов:
  - get_user_responses() / create_response()
  - check_response_exists()

Методы платежей (НОВЫЕ):
  - create_payment() → создать запись платежа
  - update_payment_status() → обновить статус
  - get_payment_by_tx() → получить платеж по ID
  - get_payments_by_user() → все платежи пользователя

📄 database/migrations/001_create_payments_table.sql
─────────────────────────────────────────────────────
SQL миграция для создания таблицы payments (НОВАЯ).
  • Структура таблицы (колонки, типы, constraints)
  • Индексы для быстрого поиска
  • Триггер для автоматического обновления updated_at


🟢 ОБРАБОТЧИКИ (HANDLERS)
═══════════════════════════════════════════════════════════════════════════

📄 handlers/payments_handler.py ← ОСНОВНОЙ ФАЙЛ ДЛЯ ПЛАТЕЖЕЙ
─────────────────────────────────────────────────────────────
Полная обработка платежей (переработан в v0.0.5).

Функции показа меню:
  - show_payment_menu() → главное меню оплаты
  - show_ton_amount_menu() → выбор суммы TON
  - show_crypto_amount_menu() → выбор суммы USDT/BTC
  - show_freekassa_amount_menu() → выбор суммы FreeKassa

Функции создания платежей:
  - create_crypto_invoice() → создать счет для валюты
  - handle_ton_amount_N() → создать счет на N TON
  - handle_dynamic_crypto_amount() → создать счет USDT/BTC
  - _fk_amount_handler() → создать ссылку FreeKassa

Функции проверки:
  - check_payment_status() → проверить статус платежа

Регистрация:
  - register_handlers() → регистрация всех callback'ов

📄 handlers/start_handler.py
────────────────────────────
Обработчик команды /start.
  • Регистрация нового пользователя
  • Показ главного меню

📄 handlers/profile_handler.py
──────────────────────────────
Обработчик профиля пользователя.
  • Показ информации профиля
  • Баланс, роль, статистика

📄 handlers/balance_handler.py
──────────────────────────────
Обработчик проверки баланса.
  • Показ текущего баланса
  • Кнопка пополнения

📄 handlers/callback_handler.py
───────────────────────────────
Обработчик callback'ов меню.
  • Навигация по меню
  • Переходы между разделами

📄 handlers/info_handler.py
───────────────────────────
Информационные разделы.
  • О проекте
  • О боте
  • Команда разработчиков
  • Планы на будущее


🟢 ИНТЕРФЕЙС
═══════════════════════════════════════════════════════════════════════════

📄 ui/menus.py
──────────────
Все меню и inline клавиатуры.

Функции меню:
  - get_main_menu() → главное меню
  - get_payment_menu() → меню оплаты (4 способа)
  - get_ton_amount_menu() → суммы TON
  - get_freekassa_amount_menu() → суммы FreeKassa
  - get_payment_confirmation_menu() → подтверждение оплаты
  - get_about_menu() / get_team_menu() / и т.д.

Все меню используют InlineKeyboardMarkup с CallbackData


🟢 ТЕСТИРОВАНИЕ
═══════════════════════════════════════════════════════════════════════════

📄 test_webhooks.py
───────────────────
Скрипт для тестирования webhook'ов (НОВЫЙ).
  • Тестирование CryptoBot webhook
  • Тестирование FreeKassa webhook
  • Тесты с невалидными подписями
  • Проверка обработки ошибок

Запуск:
  python test_webhooks.py


🟢 ДОКУМЕНТАЦИЯ
═══════════════════════════════════════════════════════════════════════════

📄 UPGRADE_TO_v0.0.5.md (НОВЫЙ)
────────────────────────────────
Полное руководство по обновлению:
  • Требования и установка
  • Конфигурация переменных окружения
  • Создание таблицы в Supabase
  • Запуск бота
  • Настройка webhook'ов
  • Примеры использования

📄 TESTING_GUIDE_v0.0.5.md (НОВЫЙ)
───────────────────────────────────
Пошаговое руководство по тестированию:
  • Подготовка окружения
  • Тестирование каждой функции
  • Проверка логов
  • Типичные ошибки и решения

📄 CHANGELOG_v0.0.0.5.md
────────────────────────
История изменений версии 0.0.5:
  • Перечисление всех реализованных функций
  • Список изменённых файлов
  • Статистика кода
  • Известные ограничения


================================================================================
ЗАВИСИМОСТИ (requirements.txt)
================================================================================

aiogram==3.13.1              — Telegram Bot API library
supabase==2.3.0              — Supabase Python SDK
python-dotenv==1.0.0         — Управление переменными окружения
aiohttp==3.9.1               — Async HTTP client/server


================================================================================
ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (.env)
================================================================================

Обязательные:
  BOT_TOKEN                  — Токен бота от @BotFather
  SUPABASE_URL               — URL проекта Supabase
  SUPABASE_KEY               — API ключ Supabase
  
Опциональные:
  CRYPTOBOT_TOKEN            — Токен CryptoBot API
  FREEKASSA_MERCHANT_ID      — ID продавца FreeKassa
  FREEKASSA_SECRET1          — Secret1 FreeKassa
  FREEKASSA_SECRET2          — Secret2 FreeKassa
  LOG_LEVEL                  — Уровень логирования (DEBUG/INFO/WARNING/ERROR)


================================================================================
БЫСТРАЯ СПРАВКА
================================================================================

Запуск бота:
  python bot.py

Тестирование webhook'ов:
  python test_webhooks.py

Просмотр логов:
  tail -f bot.log  (Unix/Mac)
  Get-Content bot.log -Tail 20 -Wait  (PowerShell)

Документация:
  - UPGRADE_TO_v0.0.5.md ← Начните отсюда
  - TESTING_GUIDE_v0.0.5.md ← Потом здесь

================================================================================
