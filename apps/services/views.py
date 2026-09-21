from rest_framework import viewsets

from apps.users.permissions import ReadOnlyOrStaff

from .models import Employee, Service
from .serializers import EmployeeSerializer, ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = (ReadOnlyOrStaff,)
    filterset_fields = ('is_active',)
    search_fields = ('name',)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.filter(is_active=True).select_related('user').prefetch_related(
        'services', 'working_hours',
    )
    serializer_class = EmployeeSerializer
    permission_classes = (ReadOnlyOrStaff,)
