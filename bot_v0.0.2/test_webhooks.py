"""
Test script for payment webhooks
Тестирование webhook'ов платежных систем

Использование:
    python test_webhooks.py
"""

import asyncio
import aiohttp
import json
import hashlib
import time
from typing import Dict, Any

# Конфигурация
WEBHOOK_HOST = "http://localhost:8080"
CRYPTOBOT_WEBHOOK_URL = f"{WEBHOOK_HOST}/webhook/cryptobot"
FREEKASSA_WEBHOOK_URL = f"{WEBHOOK_HOST}/webhook/freekassa"

# FreeKassa test credentials (замените на ваши)
FK_MERCHANT_ID = "123456"
FK_SECRET1 = "secret1_key"
FK_SECRET2 = "secret2_key"


async def test_cryptobot_webhook():
    """Тест webhook от CryptoBot"""
    print("\n🧪 Тестирование CryptoBot webhook...")
    
    payload = {
        "update_type": "invoice_paid",
        "payload": {
            "invoice_id": 123456789,
            "hash": "test_invoice_hash",
            "currency": "TON",
            "amount": "10",
            "paid_at": int(time.time()),
            "usd_rate": "5"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CRYPTOBOT_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.text()
                print(f"✓ Status: {response.status}")
                print(f"✓ Response: {result}")
                
                if response.status == 200:
                    print("✅ CryptoBot webhook успешно обработан")
                else:
                    print("❌ Ошибка при обработке CryptoBot webhook")
                    
    except Exception as e:
        print(f"❌ Ошибка подключения к CryptoBot webhook: {e}")


async def test_freekassa_webhook():
    """Тест webhook от FreeKassa"""
    print("\n🧪 Тестирование FreeKassa webhook...")
    
    # Генерируем подпись (MD5)
    order_id = f"fk_test_order_{int(time.time())}"
    amount = "100.00"
    
    sign_str = f"{FK_MERCHANT_ID}:{amount}:{FK_SECRET2}:{order_id}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    print(f"  Order ID: {order_id}")
    print(f"  Amount: {amount}")
    print(f"  Signature: {sign}")
    
    # Формируем данные для POST
    data = {
        "MERCHANT_ID": FK_MERCHANT_ID,
        "AMOUNT": amount,
        "MERCHANT_ORDER_ID": order_id,
        "SIGN": sign
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(FREEKASSA_WEBHOOK_URL, data=data) as response:
                result = await response.text()
                print(f"✓ Status: {response.status}")
                print(f"✓ Response: {result}")
                
                if response.status == 200:
                    print("✅ FreeKassa webhook успешно обработан")
                else:
                    print("❌ Ошибка при обработке FreeKassa webhook")
                    
    except Exception as e:
        print(f"❌ Ошибка подключения к FreeKassa webhook: {e}")


async def test_invalid_cryptobot_webhook():
    """Тест невалидного webhook от CryptoBot"""
    print("\n🧪 Тестирование невалидного CryptoBot webhook...")
    
    payload = {
        "update_type": "invalid_type",
        "payload": {}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CRYPTOBOT_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"✓ Status: {response.status}")
                
                if response.status >= 400:
                    print("✅ Невалидный webhook корректно отклонен")
                else:
                    print("⚠️ Невалидный webhook принят (может быть нормально)")
                    
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def test_invalid_freekassa_webhook():
    """Тест невалидного webhook от FreeKassa (неверная подпись)"""
    print("\n🧪 Тестирование невалидного FreeKassa webhook (неверная подпись)...")
    
    data = {
        "MERCHANT_ID": FK_MERCHANT_ID,
        "AMOUNT": "100.00",
        "MERCHANT_ORDER_ID": "fk_invalid_order",
        "SIGN": "invalid_signature_hash"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(FREEKASSA_WEBHOOK_URL, data=data) as response:
                print(f"✓ Status: {response.status}")
                
                if response.status >= 400:
                    print("✅ Невалидный FreeKassa webhook корректно отклонен")
                else:
                    print("⚠️ Невалидный FreeKassa webhook принят")
                    
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def main():
    """Главная функция"""
    print("=" * 60)
    print("🧪 Тестирование webhook'ов платежных систем")
    print("=" * 60)
    print(f"\nБот должен быть запущен на {WEBHOOK_HOST}")
    print("Убедитесь, что bot.py запущен перед запуском тестов")
    
    # Проверка доступности сервера
    print("\n⏳ Проверка доступности webhook сервера...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WEBHOOK_HOST}/", timeout=aiohttp.ClientTimeout(total=2)) as response:
                pass
    except Exception:
        print("❌ Webhook сервер недоступен на " + WEBHOOK_HOST)
        print("⚠️ Запустите бот: python bot.py")
        return
    
    print("✅ Webhook сервер доступен\n")
    
    # Запуск тестов
    await test_cryptobot_webhook()
    await test_freekassa_webhook()
    await test_invalid_cryptobot_webhook()
    await test_invalid_freekassa_webhook()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")
    print("=" * 60)


if __name__ == "__main__":
    print("\n💡 Для тестирования webhook'ов:")
    print("1. Запустите бот: python bot.py")
    print("2. В другом терминале: python test_webhooks.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование остановлено")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
