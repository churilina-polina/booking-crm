from django.db import models

from apps.bookings.models import Booking


class NotificationLog(models.Model):
    class Channel(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        EMAIL = 'email', 'Email'

    class Status(models.TextChoices):
        SENT = 'sent', 'Отправлено'
        FAILED = 'failed', 'Ошибка'

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=10, choices=Channel.choices)
    status = models.CharField(max_length=10, choices=Status.choices)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_channel_display()} — {self.booking} ({self.get_status_display()})'
