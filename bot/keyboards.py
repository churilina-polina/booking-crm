from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📅 Записаться')],
        [KeyboardButton(text='🗂 Мои записи')],
    ],
    resize_keyboard=True,
)


def services_keyboard(services):
    rows = [[InlineKeyboardButton(text=f'{s.name} ({s.price}₽)', callback_data=f'service:{s.id}')] for s in services]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def employees_keyboard(employees):
    rows = [
        [InlineKeyboardButton(text=e.user.get_full_name() or e.user.username, callback_data=f'employee:{e.id}')]
        for e in employees
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dates_keyboard(dates):
    rows = [[InlineKeyboardButton(text=d.strftime('%d.%m (%a)'), callback_data=f'date:{d.isoformat()}')] for d in dates]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def slots_keyboard(slots):
    rows = [[InlineKeyboardButton(text=s.strftime('%H:%M'), callback_data=f'slot:{s.isoformat()}')] for s in slots]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm:yes'),
                InlineKeyboardButton(text='❌ Отмена', callback_data='confirm:no'),
            ]
        ]
    )


def cancel_bookings_keyboard(bookings):
    rows = [
        [InlineKeyboardButton(
            text=f'{b.service.name} {b.start_time:%d.%m %H:%M}',
            callback_data=f'cancel_booking:{b.id}',
        )]
        for b in bookings
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
