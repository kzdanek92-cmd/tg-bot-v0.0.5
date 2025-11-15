"""
Payments Handler
Обработчик платежей через CryptoBot
"""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from payments.crypto import CryptoPaymentService
from payments.freekassa import FreeKassaService
from services.user_service import UserService
from services.exchange_service import convert_to_rub
from ui.menus import (
    get_payment_menu,
    get_ton_amount_menu,
    get_payment_confirmation_menu,
    get_main_menu
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

router = Router()

# Временное хранилище для счетов (в production использовать Redis или БД)
pending_invoices = {}


async def show_payment_menu(callback: CallbackQuery):
    """Показать меню выбора способа оплаты"""
    try:
        text = """
💳 <b>Пополнение баланса</b>

Выберите способ оплаты:

🪙 <b>TON</b> - быстро и без комиссий
💵 <b>USDT</b> - через CryptoBot
₿ <b>Bitcoin (BTC)</b> - через CryptoBot
💳 <b>Через FreeKassa</b> - рубли, карты, кошельки

<i>После пополнения баланс будет автоматически зачислен на ваш аккаунт</i>
"""
        await callback.message.edit_text(
            text,
            reply_markup=get_payment_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в show_payment_menu: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def show_ton_amount_menu(callback: CallbackQuery, crypto_service: CryptoPaymentService):
    """Показать меню выбора суммы в TON"""
    try:
        if not crypto_service:
            await callback.answer(
                "😔 CryptoBot не настроен. Обратитесь к администратору.",
                show_alert=True
            )
            return
            
        text = """
🪙 <b>Пополнение через TON</b>

Выберите сумму для пополнения:

<i>1 TON ≈ 50₽ (курс может меняться)</i>

После выбора суммы вы получите ссылку для оплаты через CryptoBot.
"""
        await callback.message.edit_text(
            text,
            reply_markup=get_ton_amount_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в show_ton_amount_menu: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def show_crypto_amount_menu(callback: CallbackQuery, crypto_service: CryptoPaymentService, currency: str):
    """Показать меню выбора суммы для указанной криптовалюты (динамически формируем клавиатуру)"""
    try:
        if not crypto_service:
            await callback.answer("😔 CryptoBot не настроен. Обратитесь к администратору.", show_alert=True)
            return

        text = f"\n💳 <b>Пополнение через {currency}</b>\n\nВыберите сумму для пополнения:\n\n"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"1 {currency}", callback_data=f"{currency.lower()}_amount_1"), InlineKeyboardButton(text=f"5 {currency}", callback_data=f"{currency.lower()}_amount_5")],
            [InlineKeyboardButton(text=f"10 {currency}", callback_data=f"{currency.lower()}_amount_10"), InlineKeyboardButton(text=f"25 {currency}", callback_data=f"{currency.lower()}_amount_25")],
            [InlineKeyboardButton(text=f"50 {currency}", callback_data=f"{currency.lower()}_amount_50"), InlineKeyboardButton(text=f"100 {currency}", callback_data=f"{currency.lower()}_amount_100")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в show_crypto_amount_menu: {e}")
        await callback.answer("😔 Ошибка", show_alert=True)


async def create_crypto_invoice(
    callback: CallbackQuery,
    crypto_service: CryptoPaymentService,
    user_service: UserService,
    amount: float,
    currency: str = "TON",
    description: str = None
):
    """Создать счет для оплаты в указанной криптовалюте (TON/USDT/BTC)"""
    try:
        user_id = callback.from_user.id
        if description is None:
            description = f"Пополнение баланса на {amount} {currency}"

        # Создаем счет (поддержка других валют через asset)
        invoice = await crypto_service.create_invoice(
            amount=amount,
            currency=currency,
            description=description,
            payload=str(user_id)
        )
        
        if not invoice:
            await callback.answer(
                "😔 Ошибка создания счета. Попробуйте позже.",
                show_alert=True
            )
            return
        
        # Сохраняем счет
        invoice_id = invoice.get("invoice_id") or invoice.get('id')
        pending_invoices[str(invoice_id)] = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency
        }

        # Сохраняем в Supabase
        try:
            payment_record = {
                "user_id": user_id,
                "currency": currency,
                "amount": amount,
                "tx_id": str(invoice_id),
                "status": "pending",
                "meta": invoice
            }
            # Попытка сохранить в Supabase через user_service
            try:
                await user_service.db.create_payment(payment_record)
            except Exception as e:
                logger.warning(f"Не удалось сохранить платеж в БД: {e}")
        except Exception as e:
            logger.warning(f"Не удалось сохранить платеж в БД: {e}")
        
        # Получаем ссылку для оплаты
        pay_url = crypto_service.get_payment_url(invoice)
        
        # Примерная конвертация в рубли (для TON используем курс 50₽)
        if currency == 'TON':
            rub_amount = amount * 50
            currency_display = f"{amount} TON (≈{rub_amount}₽)"
        else:
            currency_display = f"{amount} {currency}"

        text = f"""
💳 <b>Счет создан!</b>

💰 <b>Сумма:</b> {currency_display}
🆔 <b>Номер счета:</b> <code>{invoice_id}</code>

Нажмите кнопку "Оплатить" для перехода к оплате.
После оплаты нажмите "Я оплатил" для проверки платежа.

⏱ <i>Счет действителен 15 минут</i>
"""
        
        await callback.message.edit_text(
            text,
            reply_markup=get_payment_confirmation_menu(pay_url),
            parse_mode="HTML"
        )
        await callback.answer()
        logger.info(f"Создан счет {invoice_id} для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка создания счета: {e}")
        await callback.answer(
            "😔 Ошибка создания счета",
            show_alert=True
        )


async def check_payment_status(
    callback: CallbackQuery,
    crypto_service: CryptoPaymentService,
    user_service: UserService
):
    """Проверить статус платежа и зачислить баланс при успешной оплате"""
    try:
        user_id = callback.from_user.id
        
        # Находим счет пользователя (сначала в памяти, иначе в БД)
        user_invoice = None
        invoice_id = None

        for inv_id, inv_data in pending_invoices.items():
            if inv_data["user_id"] == user_id:
                user_invoice = inv_data
                invoice_id = inv_id
                break

        # Если в памяти не найдено, попробуем найти последний pending платёж в БД
        if not user_invoice:
            try:
                payments = await user_service.db.get_payments_by_user(user_id)
                for p in payments:
                    if p.get('status') == 'pending':
                        user_invoice = p
                        invoice_id = p.get('tx_id')
                        break
            except Exception:
                pass
        
        if not user_invoice:
            await callback.answer(
                "❌ Счет не найден",
                show_alert=True
            )
            return
        
        # Проверяем статус
        status = await crypto_service.check_invoice_status(invoice_id)
        
        if status == "paid":
            # Платеж прошел - начисляем баланс
            amount_crypto = user_invoice["amount"] if isinstance(user_invoice, dict) else float(user_invoice.get('amount', 0))
            currency = user_invoice["currency"] if isinstance(user_invoice, dict) else user_invoice.get('currency', 'TON')
            
            # Конвертируем в рубли с использованием текущего курса
            try:
                amount_rub = await convert_to_rub(amount_crypto, currency)
            except Exception as e:
                logger.warning(f"Error converting {currency} to RUB: {e}. Using fallback.")
                # Fallback: для TON используем 50₽
                if currency == 'TON':
                    amount_rub = amount_crypto * 50
                elif currency == 'USDT':
                    amount_rub = amount_crypto * 100
                elif currency == 'BTC':
                    amount_rub = amount_crypto * 2500000
                else:
                    amount_rub = amount_crypto  # As is

            # Обновляем баланс
            await user_service.update_balance(user_id, amount_rub)

            # Удаляем счет из pending
            if invoice_id in pending_invoices:
                del pending_invoices[invoice_id]

            # Обновляем запись в БД
            try:
                await user_service.db.update_payment_status(tx_id=str(invoice_id), updates={"status": "paid"})
            except Exception:
                pass

            text = f"""
✅ <b>Платеж успешно получен!</b>

💰 Зачислено: <b>{amount_rub:.2f}₽</b>
💱 Обменный курс: 1 {currency} = ~{amount_rub/amount_crypto:.2f}₽

Спасибо за пополнение! 🎉
"""
            await callback.message.edit_text(
                text,
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            await callback.answer("✅ Баланс пополнен!", show_alert=False)
            logger.info(f"Платеж {invoice_id} подтвержден для пользователя {user_id}")
            
        elif status == "active":
            await callback.answer(
                "⏳ Платеж еще не получен. Пожалуйста, завершите оплату.",
                show_alert=True
            )
            
        elif status == "expired":
            await callback.answer(
                "⏱ Срок действия счета истек. Создайте новый счет.",
                show_alert=True
            )
            del pending_invoices[invoice_id]
            
        else:
            await callback.answer(
                "❓ Неизвестный статус платежа",
                show_alert=True
            )
            
    except Exception as e:
        logger.error(f"Ошибка проверки платежа: {e}")
        await callback.answer(
            "😔 Ошибка проверки платежа",
            show_alert=True
        )


async def handle_coming_soon(callback: CallbackQuery, feature: str):
    """Обработчик для функций "скоро" """
    await callback.answer(
        f"🔜 {feature} будет доступен в следующих версиях!",
        show_alert=True
    )


async def handle_ton_amount_1(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 1, currency='TON')

async def handle_ton_amount_5(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 5, currency='TON')

async def handle_ton_amount_10(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 10, currency='TON')

async def handle_ton_amount_25(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 25, currency='TON')

async def handle_ton_amount_50(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 50, currency='TON')

async def handle_ton_amount_100(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    await create_crypto_invoice(callback, crypto_service, user_service, 100, currency='TON')


async def handle_dynamic_crypto_amount(callback: CallbackQuery, crypto_service: CryptoPaymentService, user_service: UserService):
    """Обработчик динамических callback'ов вида '<currency>_amount_<n>'"""
    try:
        data = callback.data  # e.g. 'usdt_amount_5'
        parts = data.split('_')
        if len(parts) >= 3 and parts[1] == 'amount':
            currency = parts[0].upper()
            try:
                amount = float(parts[2])
            except Exception:
                amount = 1.0

            await create_crypto_invoice(callback, crypto_service, user_service, amount, currency=currency)
        else:
            await callback.answer('Неверные данные', show_alert=True)

    except Exception as e:
        logger.error(f"Ошибка в handle_dynamic_crypto_amount: {e}")
        await callback.answer('Ошибка', show_alert=True)


def register_handlers(router: Router):
    """Регистрация обработчиков платежей"""
    router.callback_query.register(show_payment_menu, lambda c: c.data == "payment_menu")
    # TON
    router.callback_query.register(show_ton_amount_menu, lambda c: c.data == "pay_ton")
    # USDT/BTC dynamic menus
    async def _pay_usdt(callback: CallbackQuery, crypto_service: CryptoPaymentService):
        await show_crypto_amount_menu(callback, crypto_service, 'USDT')

    async def _pay_btc(callback: CallbackQuery, crypto_service: CryptoPaymentService):
        await show_crypto_amount_menu(callback, crypto_service, 'BTC')

    router.callback_query.register(_pay_usdt, lambda c: c.data == "pay_usdt")
    router.callback_query.register(_pay_btc, lambda c: c.data == "pay_btc")

    # FreeKassa menu
    from ui.menus import get_freekassa_amount_menu
    async def _pay_freekassa(callback: CallbackQuery):
        await callback.message.edit_text(
            "<b>Оплата через FreeKassa</b>\nВыберите сумму:",
            reply_markup=get_freekassa_amount_menu(),
            parse_mode="HTML"
        )
        await callback.answer()

    router.callback_query.register(_pay_freekassa, lambda c: c.data == "pay_freekassa")
    router.callback_query.register(check_payment_status, lambda c: c.data == "check_payment")
    
    # Обработчики выбора суммы
    router.callback_query.register(handle_ton_amount_1, lambda c: c.data == "ton_amount_1")
    router.callback_query.register(handle_ton_amount_5, lambda c: c.data == "ton_amount_5")
    router.callback_query.register(handle_ton_amount_10, lambda c: c.data == "ton_amount_10")
    router.callback_query.register(handle_ton_amount_25, lambda c: c.data == "ton_amount_25")
    router.callback_query.register(handle_ton_amount_50, lambda c: c.data == "ton_amount_50")
    router.callback_query.register(handle_ton_amount_100, lambda c: c.data == "ton_amount_100")
    # Dynamic USDT/BTC amount handlers (pattern: usdt_amount_5, btc_amount_10)
    router.callback_query.register(handle_dynamic_crypto_amount, lambda c: c.data and (c.data.startswith('usdt_amount_') or c.data.startswith('btc_amount_')))

    # FreeKassa amount handlers
    async def _fk_amount_handler(callback: CallbackQuery, freekassa_service: FreeKassaService, user_service: UserService):
        try:
            # parse amount from callback
            data = callback.data  # e.g. fk_amount_100
            parts = data.split('_')
            amount = float(parts[2]) if len(parts) >= 3 else 100.0

            # generate order id using user id + timestamp
            import time
            order_id = f"fk_{callback.from_user.id}_{int(time.time())}"
            pay_url = freekassa_service.generate_payment_link(amount=amount, order_id=order_id)

            # save payment record
            try:
                payment_record = {
                    "user_id": callback.from_user.id,
                    "currency": "RUB",
                    "amount": amount,
                    "tx_id": order_id,
                    "status": "pending",
                    "meta": {"provider": "freekassa"}
                }
                await user_service.db.create_payment(payment_record)
            except Exception as e:
                logger.warning(f"Не удалось сохранить FreeKassa платёж в БД: {e}")

            text = f"<b>Ссылка для оплаты:</b>\n{pay_url}\n\nПосле оплаты нажмите 'Проверить статус оплаты'."
            await callback.message.edit_text(text, reply_markup=get_payment_confirmation_menu(pay_url), parse_mode="HTML")
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка в FreeKassa handler: {e}")
            await callback.answer('Ошибка', show_alert=True)

    router.callback_query.register(_fk_amount_handler, lambda c: c.data and c.data.startswith('fk_amount_'))
    
    # Обработчики "скоро"
    router.callback_query.register(
        lambda c: handle_coming_soon(c, "USDT платежи"),
        lambda c: c.data == "pay_usdt_soon"
    )
    router.callback_query.register(
        lambda c: handle_coming_soon(c, "Оплата картой"),
        lambda c: c.data == "pay_card_soon"
    )

