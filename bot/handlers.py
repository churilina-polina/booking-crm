from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from . import keyboards as kb
from . import services as svc
from .states import BookingStates

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await svc.get_or_create_client(message.from_user.id, message.from_user.full_name)
    await message.answer(
        'Здравствуйте! Здесь можно записаться на услугу и посмотреть свои записи.',
        reply_markup=kb.MAIN_MENU,
    )


@router.message(F.text == '📅 Записаться')
async def start_booking(message: Message, state: FSMContext):
    services = await svc.get_active_services()
    if not services:
        await message.answer('Пока нет доступных услуг.')
        return
    await state.set_state(BookingStates.choosing_service)
    await message.answer('Выберите услугу:', reply_markup=kb.services_keyboard(services))


@router.callback_query(BookingStates.choosing_service, F.data.startswith('service:'))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split(':')[1])
    employees = await svc.get_employees_for_service(service_id)
    if not employees:
        await callback.message.edit_text('Нет доступных сотрудников для этой услуги.')
        await state.clear()
        return
    await state.update_data(service_id=service_id)
    await state.set_state(BookingStates.choosing_employee)
    await callback.message.edit_text('Выберите специалиста:', reply_markup=kb.employees_keyboard(employees))


@router.callback_query(BookingStates.choosing_employee, F.data.startswith('employee:'))
async def choose_employee(callback: CallbackQuery, state: FSMContext):
    employee_id = int(callback.data.split(':')[1])
    dates = await svc.get_available_dates(employee_id)
    if not dates:
        await callback.message.edit_text('У специалиста нет доступных дней в ближайшую неделю.')
        await state.clear()
        return
    await state.update_data(employee_id=employee_id)
    await state.set_state(BookingStates.choosing_date)
    await callback.message.edit_text('Выберите дату:', reply_markup=kb.dates_keyboard(dates))


@router.callback_query(BookingStates.choosing_date, F.data.startswith('date:'))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(':', 1)[1]
    date = datetime.fromisoformat(date_str).date()
    data = await state.get_data()
    slots = await svc.get_available_slots(data['employee_id'], data['service_id'], date)
    if not slots:
        await callback.message.edit_text('На эту дату нет свободных слотов, выберите другую.')
        return
    await state.set_state(BookingStates.choosing_time)
    await callback.message.edit_text('Выберите время:', reply_markup=kb.slots_keyboard(slots))


@router.callback_query(BookingStates.choosing_time, F.data.startswith('slot:'))
async def choose_slot(callback: CallbackQuery, state: FSMContext):
    start_time = datetime.fromisoformat(callback.data.split(':', 1)[1])
    await state.update_data(start_time=start_time.isoformat())
    await state.set_state(BookingStates.confirming)
    await callback.message.edit_text(
        f'Подтвердить запись на {start_time:%d.%m в %H:%M}?',
        reply_markup=kb.confirm_keyboard(),
    )


@router.callback_query(BookingStates.confirming, F.data == 'confirm:yes')
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    client = await svc.get_or_create_client(callback.from_user.id, callback.from_user.full_name)
    try:
        await svc.create_booking(
            client.id, data['employee_id'], data['service_id'],
            datetime.fromisoformat(data['start_time']),
        )
        await callback.message.edit_text('Запись создана! Ждём вас 🎉')
    except Exception:
        await callback.message.edit_text('Не удалось создать запись — время уже занято. Попробуйте снова.')
    await state.clear()


@router.callback_query(BookingStates.confirming, F.data == 'confirm:no')
async def cancel_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Запись отменена.')
    await state.clear()


@router.message(F.text == '🗂 Мои записи')
async def my_bookings(message: Message):
    client = await svc.get_or_create_client(message.from_user.id, message.from_user.full_name)
    bookings = await svc.get_upcoming_bookings(client.id)
    if not bookings:
        await message.answer('У вас нет предстоящих записей.')
        return
    await message.answer('Ваши записи (нажмите, чтобы отменить):', reply_markup=kb.cancel_bookings_keyboard(bookings))


@router.callback_query(F.data.startswith('cancel_booking:'))
async def cancel_booking_handler(callback: CallbackQuery):
    booking_id = int(callback.data.split(':')[1])
    client = await svc.get_or_create_client(callback.from_user.id, callback.from_user.full_name)
    await svc.cancel_booking(booking_id, client.id)
    await callback.message.edit_text('Запись отменена.')
