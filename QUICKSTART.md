# 🚀 QUICKSTART — Быстрый старт (5 минут)

**Версия:** 0.0.5  
**Последнее обновление:** 15 ноября 2025

Этот гайд поможет тебе запустить бота за 5 минут локально.

---

## 1️⃣ Установка зависимостей (1 минута)

### На Windows (PowerShell):

```powershell
cd bot_v0.0.2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### На Linux/Mac:

```bash
cd bot_v0.0.2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2️⃣ Настройка .env (1 минута)

```bash
cp .env.example .env
# Отредактируй .env в VS Code
```

### Обязательные переменные:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
CRYPTOBOT_TOKEN=487477:AAtpIbP21izkuwcDPWutkWtRfjlF3Gpbedk
LOG_LEVEL=INFO
```

---

## 3️⃣ Запуск бота (1 минута)

```bash
python bot.py
```

### Ожидаемый результат:

```
2025-11-15 14:30:45 - INFO - 🤖 Bot started successfully!
2025-11-15 14:30:45 - INFO - ✅ Supabase connected
2025-11-15 14:30:45 - INFO - 💰 CryptoBot initialized
Polling...
```

---

## 4️⃣ Тестирование (2 минуты)

1. Напиши боту `/start`
2. Нажми "💳 Пополнить баланс"
3. Выбери способ оплаты
4. Проверь Supabase → таблица `payments`

---

## 📞 Помощь?

**Telegram:** [@Danyadlyalubvi2](https://t.me/Danyadlyalubvi2)

**Дальше:** [DEPLOY_VIDEO_INSTRUCTIONS.md](./DEPLOY_VIDEO_INSTRUCTIONS.md)

---

**Удачи! 🚀**
