from rest_framework import serializers

from .models import Employee, Service, WorkingHours


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'duration_minutes', 'price', 'is_active')


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ('id', 'weekday', 'start_time', 'end_time')


class EmployeeSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    working_hours = WorkingHoursSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'full_name', 'specialization', 'services', 'working_hours', 'is_active')
        read_only_fields = ('user',)
