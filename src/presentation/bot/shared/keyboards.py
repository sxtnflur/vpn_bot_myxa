from typing import Callable, Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing_extensions import TypeVar

T = TypeVar('T')


def create_list_kb(
        objs: Iterable[T], get_btn: Callable[[T], InlineKeyboardButton], width: int = 2
) -> list[list[InlineKeyboardButton]]:
    inl_kb = [[]]
    for obj in objs:
        btn = get_btn(obj)
        if len(inl_kb[-1]) >= width:
            inl_kb.append([btn])
        else:
            inl_kb[-1].append(btn)
    return inl_kb


def one_btn_kb(text: str, callback_data: str = 'to_start'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=text, callback_data=callback_data
            )]
        ]
    )
