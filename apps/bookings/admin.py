from django.contrib import admin

from .models import Booking, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'employee', 'service', 'start_time', 'status')
    list_filter = ('status', 'employee')
    date_hierarchy = 'start_time'
    inlines = (PaymentInline,)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method')
