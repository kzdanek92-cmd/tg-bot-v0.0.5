-- ============================================================================
-- Supabase Database Schema для AI-Фриланс Ассистент v0.0.2
-- ============================================================================
-- 
-- Инструкция по применению:
-- 1. Откройте Supabase Dashboard (https://app.supabase.com)
-- 2. Выберите ваш проект
-- 3. Перейдите в SQL Editor
-- 4. Скопируйте и выполните этот скрипт
--
-- ============================================================================

-- Удаление существующих таблиц (если нужно пересоздать)
-- ВНИМАНИЕ: Это удалит все данные!
-- DROP TABLE IF EXISTS responses CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Telegram user data
    user_id BIGINT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    
    -- User stats
    balance NUMERIC(10, 2) DEFAULT 0.00 CHECK (balance >= 0),
    completed_tasks INTEGER DEFAULT 0 CHECK (completed_tasks >= 0),
    
    -- User role
    role TEXT DEFAULT 'free' CHECK (role IN ('free', 'pro')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Комментарии к таблице users
COMMENT ON TABLE users IS 'Таблица пользователей Telegram-бота';
COMMENT ON COLUMN users.id IS 'Внутренний ID (автоинкремент)';
COMMENT ON COLUMN users.user_id IS 'Telegram user ID (уникальный)';
COMMENT ON COLUMN users.username IS 'Telegram username';
COMMENT ON COLUMN users.balance IS 'Баланс пользователя в рублях';
COMMENT ON COLUMN users.completed_tasks IS 'Количество выполненных заданий';
COMMENT ON COLUMN users.role IS 'Роль пользователя (free или pro)';
COMMENT ON COLUMN users.created_at IS 'Дата регистрации пользователя';

-- ============================================================================
-- ТАБЛИЦА ОТКЛИКОВ
-- ============================================================================

CREATE TABLE IF NOT EXISTS responses (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Foreign key to users
    user_id BIGINT NOT NULL,
    
    -- Task data
    task_id INTEGER NOT NULL CHECK (task_id > 0),
    task_title TEXT NOT NULL,
    response_text TEXT NOT NULL,
    
    -- Earnings
    earned NUMERIC(10, 2) NOT NULL CHECK (earned >= 0),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Комментарии к таблице responses
COMMENT ON TABLE responses IS 'Таблица откликов пользователей на задания';
COMMENT ON COLUMN responses.id IS 'Внутренний ID отклика (автоинкремент)';
COMMENT ON COLUMN responses.user_id IS 'Telegram user ID (foreign key)';
COMMENT ON COLUMN responses.task_id IS 'ID задания';
COMMENT ON COLUMN responses.task_title IS 'Название задания';
COMMENT ON COLUMN responses.response_text IS 'Текст отклика';
COMMENT ON COLUMN responses.earned IS 'Заработано рублей за отклик';
COMMENT ON COLUMN responses.created_at IS 'Дата создания отклика';

-- ============================================================================
-- ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ ЗАПРОСОВ
-- ============================================================================

-- Индекс для быстрого поиска пользователя по user_id
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);

-- Индекс для быстрого поиска откликов по user_id
CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id);

-- Индекс для быстрого поиска откликов по task_id
CREATE INDEX IF NOT EXISTS idx_responses_task_id ON responses(task_id);

-- Уникальный индекс для предотвращения дублирования откликов
-- Один пользователь может откликнуться на задание только один раз
CREATE UNIQUE INDEX IF NOT EXISTS idx_responses_user_task 
ON responses(user_id, task_id);

-- Индекс для сортировки откликов по дате
CREATE INDEX IF NOT EXISTS idx_responses_created_at ON responses(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- 
-- Для production рекомендуется настроить RLS политики
-- Пока отключаем для упрощения разработки
--

-- Отключаем RLS для таблиц (для разработки)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE responses DISABLE ROW LEVEL SECURITY;

-- Для production раскомментируйте и настройте политики:
--
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY "Users can view their own data" ON users
--     FOR SELECT USING (auth.uid() = user_id);
--
-- CREATE POLICY "Users can update their own data" ON users
--     FOR UPDATE USING (auth.uid() = user_id);
--
-- CREATE POLICY "Users can view their own responses" ON responses
--     FOR SELECT USING (auth.uid() = user_id);
--
-- CREATE POLICY "Users can create their own responses" ON responses
--     FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- ФУНКЦИИ И ТРИГГЕРЫ (опционально)
-- ============================================================================

-- Функция для автоматического обновления updated_at (если добавите это поле)
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = NOW();
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- Триггер для users
-- CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
--     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ТЕСТОВЫЕ ДАННЫЕ (опционально, для разработки)
-- ============================================================================

-- Раскомментируйте для добавления тестовых данных:
--
-- INSERT INTO users (user_id, username, balance, completed_tasks, role) VALUES
--     (123456789, 'test_user_1', 150.00, 3, 'free'),
--     (987654321, 'test_user_2', 250.00, 5, 'pro')
-- ON CONFLICT (user_id) DO NOTHING;
--
-- INSERT INTO responses (user_id, task_id, task_title, response_text, earned) VALUES
--     (123456789, 1, 'Написать рекламный текст', 'Здравствуйте! Готов выполнить...', 50.00),
--     (123456789, 2, 'Придумать слоган', 'Привет! Задание выглядит интересно...', 50.00),
--     (987654321, 1, 'Написать рекламный текст', 'Добрый день! Имею опыт...', 50.00)
-- ON CONFLICT (user_id, task_id) DO NOTHING;

-- ============================================================================
-- ПРОВЕРКА СОЗДАННЫХ ОБЪЕКТОВ
-- ============================================================================

-- Проверка таблиц
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'responses');

-- Проверка индексов
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'responses');

-- Проверка constraints
SELECT conname, contype, conrelid::regclass AS table_name
FROM pg_constraint
WHERE conrelid IN ('users'::regclass, 'responses'::regclass);

-- ============================================================================
-- ГОТОВО!
-- ============================================================================
-- 
-- Схема базы данных успешно создана.
-- 
-- Следующие шаги:
-- 1. Проверьте, что таблицы созданы в Supabase Dashboard → Table Editor
-- 2. Скопируйте URL и API Key из Settings → API
-- 3. Добавьте их в .env файл вашего проекта
-- 4. Запустите бота и протестируйте регистрацию
--
-- ============================================================================
