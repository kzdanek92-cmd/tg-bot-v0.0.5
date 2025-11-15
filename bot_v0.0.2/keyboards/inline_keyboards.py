"""
Inline Keyboards
Inline клавиатуры для Telegram бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню бота
    
    Returns:
        InlineKeyboardMarkup с кнопками главного меню
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список заданий", callback_data="tasks_list")],
        [InlineKeyboardButton(text="✍️ Мои отклики", callback_data="my_responses")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🧾 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🔧 Настройки", callback_data="settings")]
    ])
    return keyboard


def get_registration_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для регистрации
    
    Returns:
        InlineKeyboardMarkup с кнопкой регистрации
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Зарегистрироваться", callback_data="register")]
    ])
    return keyboard


def get_tasks_keyboard(tasks: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком заданий
    
    Args:
        tasks: Список заданий
        
    Returns:
        InlineKeyboardMarkup с кнопками для каждого задания
    """
    buttons = []
    
    for task in tasks:
        button_text = f"📌 {task['title'][:40]}..."  # Ограничиваем длину
        callback_data = f"task_details_{task['id']}"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_task_details_keyboard(task_id: int, has_responded: bool = False) -> InlineKeyboardMarkup:
    """
    Клавиатура для деталей задания
    
    Args:
        task_id: ID задания
        has_responded: Откликался ли пользователь уже на это задание
        
    Returns:
        InlineKeyboardMarkup с кнопками действий
    """
    buttons = []
    
    if not has_responded:
        # Кнопка "Откликнуться" если еще не откликался
        buttons.append([InlineKeyboardButton(
            text="✍️ Откликнуться", 
            callback_data=f"task_respond_{task_id}"
        )])
    else:
        # Показываем что уже откликнулся
        buttons.append([InlineKeyboardButton(
            text="✅ Вы уже откликнулись", 
            callback_data="already_responded"
        )])
    
    # Кнопки навигации
    buttons.append([
        InlineKeyboardButton(text="◀️ К списку заданий", callback_data="tasks_list"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_back_button(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """
    Кнопка "Назад"
    
    Args:
        callback_data: Callback data для кнопки (по умолчанию main_menu)
        
    Returns:
        InlineKeyboardMarkup с кнопкой "Назад"
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data)]
    ])
    return keyboard


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для профиля пользователя
    
    Returns:
        InlineKeyboardMarkup с действиями профиля
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Проверить баланс", callback_data="balance")],
        [InlineKeyboardButton(text="✍️ Мои отклики", callback_data="my_responses")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для страницы баланса
    
    Returns:
        InlineKeyboardMarkup с действиями баланса
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Найти задания", callback_data="tasks_list")],
        [InlineKeyboardButton(text="✍️ Мои отклики", callback_data="my_responses")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_responses_keyboard(page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """
    Клавиатура для истории откликов с пагинацией
    
    Args:
        page: Текущая страница
        total_pages: Общее количество страниц
        
    Returns:
        InlineKeyboardMarkup с навигацией по страницам
    """
    buttons = []
    
    # Кнопки пагинации если больше одной страницы
    if total_pages > 1:
        pagination_row = []
        
        if page > 1:
            pagination_row.append(InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data=f"responses_page_{page-1}"
            ))
        
        pagination_row.append(InlineKeyboardButton(
            text=f"📄 {page}/{total_pages}", 
            callback_data="current_page"
        ))
        
        if page < total_pages:
            pagination_row.append(InlineKeyboardButton(
                text="Вперед ➡️", 
                callback_data=f"responses_page_{page+1}"
            ))
        
        buttons.append(pagination_row)
    
    # Кнопка возврата в меню
    buttons.append([InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для настроек (заглушка для будущих версий)
    
    Returns:
        InlineKeyboardMarkup с настройками
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Уведомления (скоро)", callback_data="settings_notifications")],
        [InlineKeyboardButton(text="🌐 Язык (скоро)", callback_data="settings_language")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])
    return keyboard


def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения действия
    
    Args:
        action: Действие для подтверждения
        item_id: ID элемента
        
    Returns:
        InlineKeyboardMarkup с кнопками подтверждения
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
        ]
    ])
    return keyboard
