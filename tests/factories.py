import factory
from factory.django import DjangoModelFactory

from apps.services.models import Employee, Service, WorkingHours
from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    role = User.Role.CLIENT


class StaffUserFactory(UserFactory):
    role = User.Role.STAFF


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Sequence(lambda n: f'Услуга {n}')
    duration_minutes = 60
    price = 1500


class EmployeeFactory(DjangoModelFactory):
    class Meta:
        model = Employee
        skip_postgeneration_save = True

    user = factory.SubFactory(StaffUserFactory)
    specialization = 'Универсал'

    @factory.post_generation
    def services(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.services.add(*extracted)


class WorkingHoursFactory(DjangoModelFactory):
    class Meta:
        model = WorkingHours

    employee = factory.SubFactory(EmployeeFactory)
    weekday = 0
    start_time = '09:00'
    end_time = '18:00'
