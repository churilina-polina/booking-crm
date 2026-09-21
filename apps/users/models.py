from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        STAFF = 'staff', 'Сотрудник'
        CLIENT = 'client', 'Клиент'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=20, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
