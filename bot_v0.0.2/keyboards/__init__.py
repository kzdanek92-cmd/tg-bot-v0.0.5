"""
Keyboard Layer
Inline клавиатуры для Telegram
"""

from .inline_keyboards import (
    get_main_menu_keyboard,
    get_registration_keyboard,
    get_tasks_keyboard,
    get_task_details_keyboard,
    get_back_button
)

__all__ = [
    'get_main_menu_keyboard',
    'get_registration_keyboard',
    'get_tasks_keyboard',
    'get_task_details_keyboard',
    'get_back_button'
]
