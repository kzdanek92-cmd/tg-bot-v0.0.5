"""
Currency Exchange Service
Сервис для получения курсов обмена валют
"""

import logging
import aiohttp
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ExchangeRateService:
    """
    Сервис для получения курсов обмена.
    
    Используется CoinGecko API (free tier, без ключа).
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Кеш курсов (в production использовать Redis)
    _cache: Dict[str, float] = {
        'TON': 50.0,      # примерный курс 1 TON ≈ 50 RUB
        'USDT': 100.0,    # примерный курс 1 USDT ≈ 100 RUB
        'BTC': 2500000.0, # примерный курс 1 BTC ≈ 2.5M RUB
    }
    
    @classmethod
    async def get_rate(cls, currency: str, target: str = "rub") -> Optional[float]:
        """
        Получить курс обмена валюты к целевой валюте (по умолчанию RUB).
        
        Args:
            currency: Коды валют (TON, BTC, ETH, USDT и т.д.)
            target: Целевая валюта (rub, usd, eur)
            
        Returns:
            Курс обмена или None при ошибке
        """
        try:
            # Для быстрого ответа используем кеш
            if currency.upper() in cls._cache:
                return cls._cache[currency.upper()]
            
            # Попытаемся получить из API
            currency_id = cls._get_coingecko_id(currency)
            if not currency_id:
                logger.warning(f"Unknown currency: {currency}")
                return None
            
            url = f"{cls.BASE_URL}/simple/price"
            params = {
                "ids": currency_id,
                "vs_currencies": target.lower(),
                "include_market_cap": "false"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        rate = data.get(currency_id, {}).get(target.lower())
                        if rate:
                            # Сохраняем в кеш
                            cls._cache[currency.upper()] = rate
                            return rate
                    else:
                        logger.warning(f"Exchange API error: {response.status}")
                        
        except Exception as e:
            logger.warning(f"Error getting exchange rate for {currency}: {e}")
        
        # Если API не сработал, вернём кешированное значение
        return cls._cache.get(currency.upper())
    
    @staticmethod
    def _get_coingecko_id(currency: str) -> Optional[str]:
        """Получить ID валюты в CoinGecko"""
        mapping = {
            'TON': 'ton',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'BNB': 'binancecoin',
        }
        return mapping.get(currency.upper())
    
    @classmethod
    def set_cache(cls, currency: str, rate: float) -> None:
        """Установить курс вручную в кеш"""
        cls._cache[currency.upper()] = rate
    
    @classmethod
    def get_cache(cls) -> Dict[str, float]:
        """Получить весь кеш курсов"""
        return cls._cache.copy()


# Функция-хелпер для конвертации
async def convert_to_rub(amount: float, currency: str) -> float:
    """
    Конвертировать сумму в рубли.
    
    Args:
        amount: Сумма в исходной валюте
        currency: Код валюты (TON, BTC, USDT и т.д.)
        
    Returns:
        Сумма в рублях
    """
    rate = await ExchangeRateService.get_rate(currency, "rub")
    if rate:
        return amount * rate
    
    # Fallback если API не доступен
    logger.warning(f"Using fallback rate for {currency}")
    return amount * ExchangeRateService._cache.get(currency.upper(), 1.0)
