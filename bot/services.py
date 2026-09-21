from django.utils import timezone

from asgiref.sync import sync_to_async


@sync_to_async
def get_active_services():
    from apps.services.models import Service

    return list(Service.objects.filter(is_active=True))


@sync_to_async
def get_employees_for_service(service_id):
    from apps.services.models import Employee

    return list(Employee.objects.filter(is_active=True, services__id=service_id).select_related('user'))


@sync_to_async
def get_available_dates(employee_id):
    from apps.bookings.availability import get_available_dates as _get_available_dates
    from apps.services.models import Employee

    employee = Employee.objects.get(id=employee_id)
    return _get_available_dates(employee)


@sync_to_async
def get_available_slots(employee_id, service_id, date):
    from apps.bookings.availability import get_available_slots as _get_available_slots
    from apps.services.models import Employee, Service

    employee = Employee.objects.get(id=employee_id)
    service = Service.objects.get(id=service_id)
    return _get_available_slots(employee, service, date)


@sync_to_async
def get_or_create_client(telegram_id, username):
    from apps.users.models import User

    user, _ = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': f'tg_{telegram_id}',
            'first_name': username or '',
            'role': User.Role.CLIENT,
        },
    )
    return user


@sync_to_async
def create_booking(client_id, employee_id, service_id, start_time):
    from apps.bookings.models import Booking, Payment
    from apps.services.models import Employee, Service
    from apps.users.models import User

    service = Service.objects.get(id=service_id)
    booking = Booking(
        client=User.objects.get(id=client_id),
        employee=Employee.objects.get(id=employee_id),
        service=service,
        start_time=start_time,
        end_time=start_time + service.duration,
    )
    booking.save()
    Payment.objects.create(booking=booking, amount=service.price)
    return booking


@sync_to_async
def get_upcoming_bookings(client_id):
    from apps.bookings.models import Booking

    return list(
        Booking.objects.filter(
            client_id=client_id,
            start_time__gte=timezone.now(),
            status__in=(Booking.Status.PENDING, Booking.Status.CONFIRMED),
        ).select_related('service', 'employee__user')
    )


@sync_to_async
def cancel_booking(booking_id, client_id):
    from apps.bookings.models import Booking

    booking = Booking.objects.get(id=booking_id, client_id=client_id)
    booking.status = Booking.Status.CANCELLED
    booking.save()
    return booking
