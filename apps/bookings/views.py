from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsOwnerOrStaff, IsStaffOrAdmin

from .models import Booking, Payment
from .serializers import BookingSerializer, PaymentSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = (IsOwnerOrStaff,)
    filterset_fields = ('status', 'employee', 'service')
    ordering_fields = ('start_time', 'created_at')

    def get_queryset(self):
        qs = Booking.objects.select_related('client', 'employee__user', 'service')
        user = self.request.user
        if user.role in ('admin', 'staff'):
            return qs
        return qs.filter(client=user)

    @action(detail=True, methods=['post'], permission_classes=(IsStaffOrAdmin,))
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'], permission_classes=(IsStaffOrAdmin,))
    def complete(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.COMPLETED
        booking.save()
        return Response(self.get_serializer(booking).data)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (IsStaffOrAdmin,)
    queryset = Payment.objects.select_related('booking')

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        payment = self.get_object()
        payment.status = Payment.Status.PAID
        payment.paid_at = timezone.now()
        payment.save()
        return Response(self.get_serializer(payment).data)
