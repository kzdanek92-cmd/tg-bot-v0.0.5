# 🚀 Развертывание бота

## Вариант 1: Локальный запуск (для разработки)

### Windows

```bash
# 1. Установить Python 3.8+
# Скачать с https://www.python.org/downloads/

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать
venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Настроить токен в bot.py

# 6. Запустить
python bot.py
```

### Linux/Mac

```bash
# 1. Установить Python 3.8+
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                   # Mac

# 2. Создать виртуальное окружение
python3 -m venv venv

# 3. Активировать
source venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Настроить токен в bot.py

# 6. Запустить
python bot.py
```

---

## Вариант 2: Запуск на сервере (VPS)

### Подготовка сервера

```bash
# Подключиться к серверу
ssh user@your-server.com

# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Python и Git
sudo apt install python3 python3-pip python3-venv git -y

# Клонировать проект
git clone https://github.com/your-repo/freelance-bot.git
cd freelance-bot

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Настройка переменных окружения

```bash
# Создать .env файл
nano .env

# Добавить:
BOT_TOKEN=your_bot_token_here
```

### Запуск через systemd (автозапуск)

```bash
# Создать service файл
sudo nano /etc/systemd/system/freelance-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Freelance Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/freelance-bot
Environment="PATH=/home/your_username/freelance-bot/venv/bin"
ExecStart=/home/your_username/freelance-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустить сервис:
```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Запустить бота
sudo systemctl start freelance-bot

# Включить автозапуск
sudo systemctl enable freelance-bot

# Проверить статус
sudo systemctl status freelance-bot

# Посмотреть логи
sudo journalctl -u freelance-bot -f
```

---

## Вариант 3: Docker

### Создать Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY . .

# Запустить бота
CMD ["python", "bot.py"]
```

### Запуск

```bash
# Собрать образ
docker build -t freelance-bot .

# Запустить контейнер
docker run -d \
  --name freelance-bot \
  --restart unless-stopped \
  -e BOT_TOKEN=your_token_here \
  -v $(pwd)/user_data.json:/app/user_data.json \
  freelance-bot

# Посмотреть логи
docker logs -f freelance-bot

# Остановить
docker stop freelance-bot

# Удалить
docker rm freelance-bot
```

---

## Вариант 4: Docker Compose

### Создать docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: freelance-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./user_data.json:/app/user_data.json
```

### Запуск

```bash
# Создать .env файл
echo "BOT_TOKEN=your_token_here" > .env

# Запустить
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

---

## Вариант 5: Heroku

### Подготовка

```bash
# Установить Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Войти
heroku login

# Создать приложение
heroku create your-bot-name
```

### Создать Procfile

```
worker: python bot.py
```

### Создать runtime.txt

```
python-3.11.0
```

### Развернуть

```bash
# Добавить токен
heroku config:set BOT_TOKEN=your_token_here

# Отправить код
git add .
git commit -m "Initial commit"
git push heroku main

# Запустить worker
heroku ps:scale worker=1

# Посмотреть логи
heroku logs --tail
```

---

## Мониторинг

### Проверка работы бота

```bash
# Локально
# Просто отправь /start в Telegram

# На сервере
sudo systemctl status freelance-bot

# Docker
docker ps | grep freelance-bot
docker logs freelance-bot

# Heroku
heroku ps
heroku logs --tail
```

### Автоматический перезапуск при падении

**systemd:** Уже настроен через `Restart=always`

**Docker:** Используй `--restart unless-stopped`

**Heroku:** Автоматически перезапускает

---

## Обновление бота

### Локально

```bash
# Остановить (Ctrl+C)
# Обновить код
git pull
# Запустить снова
python bot.py
```

### На сервере (systemd)

```bash
# Остановить
sudo systemctl stop freelance-bot

# Обновить код
cd /home/your_username/freelance-bot
git pull

# Запустить
sudo systemctl start freelance-bot
```

### Docker

```bash
# Остановить и удалить
docker-compose down

# Обновить код
git pull

# Пересобрать и запустить
docker-compose up -d --build
```

---

## Резервное копирование

### Бэкап данных

```bash
# Локально
cp user_data.json user_data.backup.json

# На сервере
scp user@server:/path/to/user_data.json ./backup/

# Docker
docker cp freelance-bot:/app/user_data.json ./backup/
```

### Автоматический бэкап (cron)

```bash
# Открыть crontab
crontab -e

# Добавить (бэкап каждый день в 3:00)
0 3 * * * cp /home/user/freelance-bot/user_data.json /home/user/backups/user_data_$(date +\%Y\%m\%d).json
```

---

## Безопасность

### Не коммить токен в Git

```bash
# Добавить в .gitignore
echo ".env" >> .gitignore
echo "user_data.json" >> .gitignore

# Использовать переменные окружения
export BOT_TOKEN=your_token_here
```

### Ограничить доступ к файлам

```bash
chmod 600 user_data.json
chmod 600 .env
```

---

## Troubleshooting

### Бот не отвечает

1. Проверь, что бот запущен
2. Проверь токен
3. Проверь интернет-соединение
4. Посмотри логи

### Ошибка "Invalid token"

- Проверь токен от @BotFather
- Убедись, что нет лишних пробелов

### Ошибка "Module not found"

```bash
pip install -r requirements.txt
```

### Данные не сохраняются

- Проверь права на запись
- Проверь, что файл user_data.json создается
- Посмотри логи на ошибки

---

## Рекомендации

### Для разработки:
- ✅ Локальный запуск
- ✅ Виртуальное окружение

### Для тестирования:
- ✅ VPS с systemd
- ✅ Docker

### Для продакшена:
- ✅ Docker Compose
- ✅ Kubernetes (для масштабирования)
- ✅ Мониторинг (Prometheus + Grafana)
- ✅ Автоматические бэкапы
