from django.contrib import admin

from .models import Employee, Service, WorkingHours


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_active')
    filter_horizontal = ('services',)
    inlines = (WorkingHoursInline,)
