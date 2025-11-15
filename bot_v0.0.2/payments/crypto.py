"""
CryptoBot Payment Service
Сервис для работы с CryptoBot API (TON платежи)
"""

import logging
import aiohttp
from typing import Optional, Dict, Any
from decimal import Decimal

logger = logging.getLogger(__name__)


class CryptoPaymentService:
    """
    Сервис для работы с CryptoBot API
    
    Документация: https://help.crypt.bot/crypto-pay-api
    """
    
    def __init__(self, api_token: str):
        """
        Инициализация сервиса
        
        Args:
            api_token: API токен от CryptoBot (@CryptoBot -> /api)
        """
        self.api_token = api_token
        self.base_url = "https://pay.crypt.bot/api"
        self.headers = {
            "Crypto-Pay-API-Token": api_token
        }
        logger.info("CryptoPaymentService инициализирован")
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = "TON",
        description: str = "Пополнение баланса",
        payload: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Создание счета для оплаты
        
        Args:
            amount: Сумма платежа
            currency: Валюта (TON, BTC, ETH, USDT, etc.)
            description: Описание платежа
            payload: Дополнительные данные (например, user_id)
            
        Returns:
            Словарь с данными счета или None при ошибке
        """
        try:
            url = f"{self.base_url}/createInvoice"
            
            data = {
                "amount": str(amount),
                "currency_type": "crypto",
                "asset": currency,
                "description": description,
            }
            
            if payload:
                data["payload"] = payload
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            invoice_data = result.get("result", {})
                            logger.info(f"Счет создан: {invoice_data.get('invoice_id')}")
                            return invoice_data
                        else:
                            logger.error(f"Ошибка создания счета: {result}")
                            return None
                    else:
                        logger.error(f"HTTP ошибка {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка создания счета: {e}")
            return None
    
    async def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение информации о счете
        
        Args:
            invoice_id: ID счета
            
        Returns:
            Словарь с данными счета или None при ошибке
        """
        try:
            url = f"{self.base_url}/getInvoices"
            
            params = {
                "invoice_ids": invoice_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            invoices = result.get("result", {}).get("items", [])
                            if invoices:
                                return invoices[0]
                        return None
                    else:
                        logger.error(f"HTTP ошибка {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка получения счета: {e}")
            return None
    
    async def check_invoice_status(self, invoice_id: int) -> Optional[str]:
        """
        Проверка статуса счета
        
        Args:
            invoice_id: ID счета
            
        Returns:
            Статус счета (active, paid, expired) или None при ошибке
        """
        invoice = await self.get_invoice(invoice_id)
        if invoice:
            return invoice.get("status")
        return None
    
    async def get_balance(self) -> Optional[Dict[str, Any]]:
        """
        Получение баланса CryptoBot аккаунта
        
        Returns:
            Словарь с балансами по валютам или None при ошибке
        """
        try:
            url = f"{self.base_url}/getBalance"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            return result.get("result", [])
                        return None
                    else:
                        logger.error(f"HTTP ошибка {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return None
    
    async def get_exchange_rates(self) -> Optional[Dict[str, Any]]:
        """
        Получение курсов обмена
        
        Returns:
            Словарь с курсами валют или None при ошибке
        """
        try:
            url = f"{self.base_url}/getExchangeRates"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            return result.get("result", [])
                        return None
                    else:
                        logger.error(f"HTTP ошибка {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка получения курсов: {e}")
            return None
    
    def get_payment_url(self, invoice_data: Dict[str, Any]) -> str:
        """
        Получение ссылки для оплаты
        
        Args:
            invoice_data: Данные счета из create_invoice
            
        Returns:
            URL для оплаты
        """
        return invoice_data.get("pay_url", "")
    
    async def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Проверка webhook от CryptoBot
        
        Args:
            data: Данные webhook
            
        Returns:
            True если webhook валиден
        """
        # В production нужно проверять подпись
        # Для простоты пока просто проверяем наличие нужных полей
        required_fields = ["update_type", "payload"]
        return all(field in data for field in required_fields)
