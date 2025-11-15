#!/usr/bin/env python3
"""
🌐 Запуск бота с ngrok туннелем для локального тестирования
Создает публичный URL для webhook'ов FreeKassa
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем папку бота в path
bot_dir = Path(__file__).parent / "bot_v0.0.2"
sys.path.insert(0, str(bot_dir))

from pyngrok import ngrok
from dotenv import load_dotenv

# Загружаем переменные окружения
def safe_load_dotenv(path):
    try:
        load_dotenv(path, encoding="utf-8")
        return True
    except UnicodeDecodeError:
        print("⚠️ .env содержит символы в неподдерживаемой кодировке. Попробую безопасно прочитать файл...")
        try:
            # Попробуем прочитать файл как байты и декодировать с заменой ошибок
            raw = (bot_dir / ".env").read_bytes()
            text = raw.decode("utf-8", errors="replace")
            sanitized = bot_dir / ".env.sanitized"
            sanitized.write_text(text, encoding="utf-8")
            load_dotenv(sanitized, encoding="utf-8")
            print("✅ .env загружен из .env.sanitized (заменены некорректные символы)")
            return True
        except Exception as e:
            print(f"❌ Не удалось безопасно загрузить .env: {e}")
            return False


safe_load_dotenv(bot_dir / ".env")

async def main():
    print("🌐 Инициализация ngrok туннеля...")
    
    try:
        # Запускаем ngrok для порта 8080
        public_url = ngrok.connect(8080, "http")
        print(f"\n✅ Туннель создан!")
        print(f"🔗 Публичный URL: {public_url}")
        print(f"\n📋 Используй этот URL в FreeKassa:")
        print(f"   URL ОПОВЕЩЕНИЯ: {public_url}/webhook/freekassa")
        print(f"   URL УСПЕШНОЙ ОПЛАТЫ: {public_url}/payment-success")
        print(f"   URL ВОЗВРАТА: {public_url}/payment-failed")
        
        # Сохраняем URL в .env если нужно
        env_file = bot_dir / ".env"
        if env_file.exists():
            with open(env_file, "a") as f:
                f.write(f"\n# Ngrok URL для локального тестирования\n")
                f.write(f"PUBLIC_URL={public_url}\n")
        
        print(f"\n🤖 Попытка запустить бот на порте 8080...")
        print(f"⏳ Подождите, пробую инициализировать бота...")

        try:
            # Импортируем и запускаем бота
            from bot import main as bot_main
            await bot_main()
        except KeyboardInterrupt:
            print("\n\n🛑 Остановка бота (KeyboardInterrupt)...")
        except Exception as e:
            import traceback
            print("\n❌ При запуске бота произошла ошибка:")
            traceback.print_exc()
            print("\n⚠️ Бот не запущен, но туннель ngrok остаётся активным.")
            print("   Ты можешь запустить бот вручную в другом окне терминала:")
            print("\n   cd \"c:\\Users\\kzdan\\OneDrive\\Desktop\\Новая папка\"")
            print("   python bot_v0.0.2\\bot.py\n")
            print("   Или исправить ошибку в коде и перезапустить этот скрипт.")
            # Ожидание, чтобы туннель оставался открытым для тестов
            try:
                print("\nНажми Ctrl+C чтобы остановить и закрыть туннель.")
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Остановка туннеля по Ctrl+C...")
        finally:
            ngrok.kill()
            print("✅ Туннель закрыт")
    except Exception as e:
        print(f"❌ Ошибка при инициализации туннеля или сохранении .env: {e}")
        try:
            ngrok.kill()
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BOT LAUNCHER WITH NGROK")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Завершено")
