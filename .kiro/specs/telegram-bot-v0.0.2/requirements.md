# Requirements Document - Telegram Bot Version 0.0.2

## Introduction

Версия 0.0.2 AI-Фриланс Ассистента представляет собой значительное улучшение прототипа 0.0.1. Основная цель — добавить систему регистрации пользователей, профили, интеграцию с Supabase в качестве базы данных и улучшить пользовательский интерфейс через inline-кнопки. Все функции версии 0.0.1 должны быть сохранены и улучшены.

## Glossary

- **System**: Telegram-бот AI-Фриланс Ассистент
- **User**: Пользователь Telegram, взаимодействующий с ботом
- **Supabase**: Облачная база данных PostgreSQL с REST API
- **Inline Keyboard**: Интерактивные кнопки в Telegram-сообщениях
- **Profile**: Профиль пользователя с персональными данными
- **Free Role**: Базовая роль пользователя по умолчанию
- **Pro Role**: Премиум роль пользователя (для будущих версий)
- **Task Response**: Отклик пользователя на фриланс-задание
- **Balance**: Виртуальный баланс пользователя в рублях

## Requirements

### Requirement 1: Регистрация пользователя

**User Story:** Как новый пользователь, я хочу зарегистрироваться в системе при первом запуске, чтобы бот мог сохранять мои данные и прогресс

#### Acceptance Criteria

1. WHEN User sends /start command for the first time, THE System SHALL check if User exists in database
2. IF User does not exist in database, THEN THE System SHALL display registration prompt with username from Telegram
3. WHEN User confirms registration, THE System SHALL create new user record in Supabase users table
4. THE System SHALL store user_id, username, balance (0), completed_tasks (0), role (free), and created_at timestamp
5. WHEN registration completes successfully, THE System SHALL display welcome message with profile information

### Requirement 2: Система профилей пользователя

**User Story:** Как зарегистрированный пользователь, я хочу просматривать и управлять своим профилем, чтобы отслеживать свой прогресс и статистику

#### Acceptance Criteria

1. THE System SHALL store user profile with fields: user_id, username, balance, completed_tasks, role, created_at
2. WHEN User sends /profile command, THE System SHALL retrieve user data from Supabase database
3. THE System SHALL display profile information in formatted message with emoji and structure
4. THE System SHALL show inline keyboard buttons for profile actions (view balance, view responses, settings)
5. WHEN User data is not found, THE System SHALL prompt User to register

### Requirement 3: Inline-кнопки для навигации

**User Story:** Как пользователь, я хочу использовать удобные кнопки вместо текстовых команд, чтобы быстрее взаимодействовать с ботом

#### Acceptance Criteria

1. WHEN User sends /start command, THE System SHALL display main menu with inline keyboard
2. THE System SHALL provide inline buttons: "📋 Список заданий", "✍️ Мои отклики", "💰 Баланс", "🧾 Профиль", "🔧 Настройки"
3. WHEN User clicks "📋 Список заданий" button, THE System SHALL display available tasks with inline buttons for each task
4. WHEN User clicks task button, THE System SHALL show task details with "Откликнуться" button
5. WHEN User clicks "Откликнуться" button, THE System SHALL generate and send response for selected task
6. WHEN User clicks "💰 Баланс" button, THE System SHALL display current balance and statistics
7. WHEN User clicks "🧾 Профиль" button, THE System SHALL display user profile information
8. WHEN User clicks "🔧 Настройки" button, THE System SHALL display placeholder message for future functionality
9. THE System SHALL provide "◀️ Назад" button on all sub-menus to return to main menu

### Requirement 4: Интеграция с Supabase

**User Story:** Как система, я должна использовать Supabase для хранения данных пользователей, чтобы обеспечить надежное и масштабируемое хранение информации

#### Acceptance Criteria

1. THE System SHALL connect to Supabase using API client with URL and API key
2. THE System SHALL create users table with columns: id (primary key), user_id (bigint unique), username (text), balance (numeric), completed_tasks (integer), role (text), created_at (timestamp)
3. THE System SHALL create responses table with columns: id (primary key), user_id (bigint), task_id (integer), task_title (text), response_text (text), earned (numeric), created_at (timestamp)
4. WHEN User registers, THE System SHALL insert new record into users table
5. WHEN User sends task response, THE System SHALL insert new record into responses table
6. WHEN User balance changes, THE System SHALL update balance field in users table
7. THE System SHALL use Supabase queries instead of JSON file operations
8. IF Supabase connection fails, THEN THE System SHALL log error and display user-friendly error message

### Requirement 5: Обновление баланса в базе данных

**User Story:** Как пользователь, я хочу чтобы мой баланс автоматически обновлялся после выполнения заданий, чтобы видеть актуальную информацию

#### Acceptance Criteria

1. WHEN User successfully sends task response, THE System SHALL increment balance by 50 rubles in Supabase
2. THE System SHALL increment completed_tasks counter by 1 in Supabase
3. WHEN balance update completes, THE System SHALL display updated balance to User
4. THE System SHALL use atomic database operations to prevent race conditions
5. IF database update fails, THEN THE System SHALL rollback response creation and notify User

### Requirement 6: Проверка регистрации пользователя

**User Story:** Как система, я должна проверять регистрацию пользователя перед выполнением действий, чтобы обеспечить корректную работу с данными

#### Acceptance Criteria

1. WHEN User sends any command except /start, THE System SHALL check if User exists in database
2. IF User is not registered, THEN THE System SHALL display registration prompt with /start command
3. THE System SHALL prevent unregistered users from accessing tasks, balance, and profile features
4. WHEN User completes registration, THE System SHALL allow access to all features

### Requirement 7: Обработка ошибок

**User Story:** Как пользователь, я хочу получать понятные сообщения об ошибках, чтобы понимать что пошло не так и как это исправить

#### Acceptance Criteria

1. WHEN database connection error occurs, THE System SHALL display message "⚠️ Ошибка подключения к базе данных. Попробуйте позже."
2. WHEN unexpected error occurs, THE System SHALL log error details and display generic error message to User
3. THE System SHALL handle Supabase API errors gracefully without crashing
4. WHEN User performs invalid action, THE System SHALL display helpful error message with guidance
5. THE System SHALL log all errors with timestamp and user context for debugging

### Requirement 8: Миграция данных из JSON

**User Story:** Как разработчик, я хочу сохранить существующие данные пользователей при переходе на Supabase, чтобы не потерять информацию из версии 0.0.1

#### Acceptance Criteria

1. THE System SHALL provide migration script to transfer data from user_data.json to Supabase
2. WHEN migration script runs, THE System SHALL read all users from JSON file
3. THE System SHALL insert each user into Supabase users table
4. THE System SHALL insert all user responses into Supabase responses table
5. WHEN migration completes, THE System SHALL display summary of migrated records

### Requirement 9: Обратная совместимость команд

**User Story:** Как существующий пользователь, я хочу продолжать использовать текстовые команды, чтобы не переучиваться на новый интерфейс

#### Acceptance Criteria

1. THE System SHALL support all commands from version 0.0.1: /start, /tasks, /respond, /balance, /my_responses
2. WHEN User sends text command, THE System SHALL execute same functionality as inline button
3. THE System SHALL display inline keyboard after executing text command
4. THE System SHALL maintain backward compatibility with /respond <task_id> syntax

### Requirement 10: Улучшенный интерфейс списка заданий

**User Story:** Как пользователь, я хочу видеть задания в удобном формате с кнопками, чтобы быстро выбирать интересующие меня задания

#### Acceptance Criteria

1. WHEN User requests task list, THE System SHALL display each task as separate message or paginated list
2. THE System SHALL show inline button "Подробнее" for each task
3. WHEN User clicks "Подробнее", THE System SHALL display full task details with "Откликнуться" button
4. WHEN User clicks "Откликнуться", THE System SHALL check if User already responded to this task
5. IF User already responded, THEN THE System SHALL display warning message
6. IF User has not responded, THEN THE System SHALL generate response and update database
