"""
UI Menus
Обновленные меню для версии 0.0.4
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """
    Главное меню бота (обновленное для v0.0.4)
    
    Returns:
        InlineKeyboardMarkup с главным меню
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="⚙️ Автоматический заработок", callback_data="auto_earn")],
        [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="payment_menu")],
        [InlineKeyboardButton(text="📜 Соглашение", callback_data="agreement")],
        [InlineKeyboardButton(text="🧱 О проекте", callback_data="about_project")],
        [InlineKeyboardButton(text="👑 Команда / Разработчики", callback_data="team")],
        [InlineKeyboardButton(text="🚀 Планы на будущее", callback_data="future_plans")]
    ])
    return keyboard


def get_payment_menu() -> InlineKeyboardMarkup:
    """
    Меню выбора способа оплаты
    
    Returns:
        InlineKeyboardMarkup с вариантами оплаты
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Оплатить TON", callback_data="pay_ton")],
        [InlineKeyboardButton(text="💎 Оплатить USDT", callback_data="pay_usdt")],
        [InlineKeyboardButton(text="₿ Оплатить BTC", callback_data="pay_btc")],
        [InlineKeyboardButton(text="💳 Оплатить через FreeKassa", callback_data="pay_freekassa")],
        [InlineKeyboardButton(text="🔎 Проверить статус оплаты", callback_data="check_payment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ])
    return keyboard


def get_ton_amount_menu() -> InlineKeyboardMarkup:
    """
    Меню выбора суммы пополнения в TON
    
    Returns:
        InlineKeyboardMarkup с вариантами сумм
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 TON", callback_data="ton_amount_1"),
            InlineKeyboardButton(text="5 TON", callback_data="ton_amount_5")
        ],
        [
            InlineKeyboardButton(text="10 TON", callback_data="ton_amount_10"),
            InlineKeyboardButton(text="25 TON", callback_data="ton_amount_25")
        ],
        [
            InlineKeyboardButton(text="50 TON", callback_data="ton_amount_50"),
            InlineKeyboardButton(text="100 TON", callback_data="ton_amount_100")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
    ])
    return keyboard


def get_freekassa_amount_menu() -> InlineKeyboardMarkup:
    """
    Меню выбора суммы для FreeKassa (в рублях)
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="100 ₽", callback_data="fk_amount_100"),
            InlineKeyboardButton(text="250 ₽", callback_data="fk_amount_250")
        ],
        [
            InlineKeyboardButton(text="500 ₽", callback_data="fk_amount_500"),
            InlineKeyboardButton(text="1000 ₽", callback_data="fk_amount_1000")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
    ])
    return keyboard


def get_payment_confirmation_menu(pay_url: str) -> InlineKeyboardMarkup:
    """
    Меню подтверждения платежа
    
    Args:
        pay_url: Ссылка на оплату
        
    Returns:
        InlineKeyboardMarkup с кнопкой оплаты
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="payment_menu")]
    ])
    return keyboard


def get_about_menu() -> InlineKeyboardMarkup:
    """
    Меню раздела "О проекте"
    
    Returns:
        InlineKeyboardMarkup с кнопкой возврата
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Команда", callback_data="team")],
        [InlineKeyboardButton(text="🚀 Планы", callback_data="future_plans")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_team_menu() -> InlineKeyboardMarkup:
    """
    Меню раздела "Команда"
    
    Returns:
        InlineKeyboardMarkup с контактами
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Связаться с разработчиком", url="https://t.me/Danyadlyalubvi2")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_future_menu() -> InlineKeyboardMarkup:
    """
    Меню раздела "Планы на будущее"
    
    Returns:
        InlineKeyboardMarkup с кнопкой возврата
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧱 О проекте", callback_data="about_project")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_auto_earn_menu() -> InlineKeyboardMarkup:
    """
    Меню автоматического заработка
    
    Returns:
        InlineKeyboardMarkup с опциями
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список заданий", callback_data="tasks_list")],
        [InlineKeyboardButton(text="✍️ Мои отклики", callback_data="my_responses")],
        [InlineKeyboardButton(text="⚙️ Настройки (скоро)", callback_data="auto_settings_soon")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_agreement_menu() -> InlineKeyboardMarkup:
    """
    Меню соглашения
    
    Returns:
        InlineKeyboardMarkup с кнопками
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принимаю", callback_data="accept_agreement")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard
