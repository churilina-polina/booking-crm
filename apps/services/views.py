from datetime import datetime

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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
    queryset = (
        Employee.objects.filter(is_active=True)
        .select_related('user')
        .prefetch_related(
            'services',
            'working_hours',
        )
    )
    serializer_class = EmployeeSerializer
    permission_classes = (ReadOnlyOrStaff,)

    @action(detail=True, methods=['get'], permission_classes=(permissions.IsAuthenticated,))
    def available_slots(self, request, pk=None):
        from apps.bookings.availability import get_available_slots

        employee = self.get_object()
        service_id = request.query_params.get('service')
        date_str = request.query_params.get('date')
        if not service_id or not date_str:
            raise ValidationError('Параметры "service" и "date" обязательны.')

        try:
            service = employee.services.get(id=service_id)
        except Service.DoesNotExist:
            raise ValidationError('Эта услуга недоступна у данного сотрудника.')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError('Дата должна быть в формате YYYY-MM-DD.')

        slots = get_available_slots(employee, service, date)
        return Response([slot.isoformat() for slot in slots])
