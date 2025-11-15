"""
FreeKassa Payment Helper

Поддерживает генерацию ссылки на оплату и верификацию уведомлений (callback).

Документация FreeKassa: https://www.free-kassa.ru/
"""
import hashlib
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FreeKassaService:
    def __init__(self, merchant_id: str, secret1: str, secret2: str, base_url: str = "https://www.free-kassa.ru/merchant/cash.php"):
        self.merchant_id = merchant_id
        self.secret1 = secret1
        self.secret2 = secret2
        self.base_url = base_url

    def generate_payment_link(self, amount: float, order_id: str, currency: str = 'RUB', desc: str = '') -> str:
        """
        Сгенерировать ссылку для перехода на FreeKassa

        Формула подписи: MD5(merchant_id:amount:secret1:order_id)
        """
        # Формат суммы с двумя знаками
        amount_str = f"{amount:.2f}"
        sign_str = f"{self.merchant_id}:{amount_str}:{self.secret1}:{order_id}"
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        # Сформируем URL
        params = f"m={self.merchant_id}&oa={amount_str}&o={order_id}&s={sign}"
        if desc:
            params += f"&desc={desc}"

        return f"{self.base_url}?{params}"

    def verify_notification(self, data: Dict[str, Any]) -> bool:
        """
        Проверить уведомление от FreeKassa.

        FreeKassa присылает параметры, среди которых ожидается 'MERCHANT_ID', 'AMOUNT', 'MERCHANT_ORDER_ID' и 'SIGN'
        Рассчитываем подпись как MD5(merchant_id:amount:secret2:merchant_order_id)
        (используем secret2 для проверки уведомлений)
        """
        try:
            merchant = data.get('MERCHANT_ID') or data.get('m')
            amount = data.get('AMOUNT') or data.get('oa') or data.get('AMOUNT')
            order = data.get('MERCHANT_ORDER_ID') or data.get('o') or data.get('MERCHANT_ORDER_ID')
            sign = data.get('SIGN') or data.get('s')

            if not (merchant and amount and order and sign):
                logger.warning('Недостаточно данных для проверки FreeKassa уведомления')
                return False

            check_str = f"{merchant}:{amount}:{self.secret2}:{order}"
            calc = hashlib.md5(check_str.encode('utf-8')).hexdigest()

            valid = calc == sign
            if not valid:
                logger.warning(f"FreeKassa verification failed: expected {calc}, got {sign}")
            return valid

        except Exception as e:
            logger.error(f"Ошибка верификации FreeKassa уведомления: {e}")
            return False
