from datetime import timedelta

from django.conf import settings
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text='Продолжительность услуги в минутах')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def duration(self):
        return timedelta(minutes=self.duration_minutes)


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        limit_choices_to={'role': 'staff'},
    )
    specialization = models.CharField(max_length=200, blank=True)
    services = models.ManyToManyField(Service, related_name='employees', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)


class WorkingHours(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Понедельник'
        TUESDAY = 1, 'Вторник'
        WEDNESDAY = 2, 'Среда'
        THURSDAY = 3, 'Четверг'
        FRIDAY = 4, 'Пятница'
        SATURDAY = 5, 'Суббота'
        SUNDAY = 6, 'Воскресенье'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='working_hours')
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('employee', 'weekday')
        ordering = ('weekday', 'start_time')

    def __str__(self):
        return f'{self.employee} — {self.get_weekday_display()} {self.start_time}-{self.end_time}'
