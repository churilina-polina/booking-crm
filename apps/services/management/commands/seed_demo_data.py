from django.core.management.base import BaseCommand

from apps.services.models import Employee, Service, WorkingHours
from apps.users.models import User


class Command(BaseCommand):
    help = 'Populate the database with demo services, staff and working hours.'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created superuser "admin" / "admin12345"'))

        services_data = [
            ('Стрижка', 60, 1500),
            ('Маникюр', 90, 2000),
            ('Массаж', 60, 2500),
        ]
        services = []
        for name, duration, price in services_data:
            service, _ = Service.objects.get_or_create(
                name=name, defaults={'duration_minutes': duration, 'price': price},
            )
            services.append(service)

        staff_user, created = User.objects.get_or_create(
            username='master_anna',
            defaults={'role': User.Role.STAFF, 'first_name': 'Анна', 'last_name': 'Мастерова'},
        )
        if created:
            staff_user.set_password('staff12345')
            staff_user.save()

        employee, _ = Employee.objects.get_or_create(user=staff_user, defaults={'specialization': 'Универсал'})
        employee.services.set(services)

        for weekday in range(5):  # Mon-Fri
            WorkingHours.objects.get_or_create(
                employee=employee, weekday=weekday,
                defaults={'start_time': '09:00', 'end_time': '18:00'},
            )

        self.stdout.write(self.style.SUCCESS('Demo data is ready.'))
