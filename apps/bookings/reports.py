import csv

from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from apps.users.permissions import IsStaffOrAdmin

from .models import Booking, Payment

PERIOD_PARAMS = [
    OpenApiParameter(
        'date_from', OpenApiTypes.DATE, description='Начало периода (по умолчанию — начало текущего месяца)'
    ),
    OpenApiParameter('date_to', OpenApiTypes.DATE, description='Конец периода (по умолчанию — сегодня)'),
]


def _parse_period(request):
    """Return (date_from, date_to) parsed from query params, defaulting to the current month."""
    today = timezone.localdate()
    date_from = parse_date(request.query_params.get('date_from', '')) or today.replace(day=1)
    date_to = parse_date(request.query_params.get('date_to', '')) or today
    return date_from, date_to


@extend_schema(tags=['reports'], parameters=PERIOD_PARAMS, responses=OpenApiTypes.OBJECT)
class RevenueReportView(APIView):
    """Revenue and booking counts by status for a given period (defaults to current month)."""

    permission_classes = (IsStaffOrAdmin,)

    def get(self, request):
        date_from, date_to = _parse_period(request)

        bookings_qs = Booking.objects.filter(start_time__date__range=(date_from, date_to))
        by_status = bookings_qs.values('status').annotate(count=Count('id')).order_by('status')

        revenue = (
            Payment.objects.filter(
                status=Payment.Status.PAID,
                booking__start_time__date__range=(date_from, date_to),
            ).aggregate(total=Sum('amount'))['total']
            or 0
        )

        return Response(
            {
                'date_from': date_from,
                'date_to': date_to,
                'total_revenue': revenue,
                'bookings_by_status': list(by_status),
                'total_bookings': bookings_qs.count(),
            }
        )


@extend_schema(tags=['reports'], parameters=PERIOD_PARAMS, responses=OpenApiTypes.OBJECT)
class EmployeeLoadReportView(APIView):
    """Bookings count and revenue per employee for a given period."""

    permission_classes = (IsStaffOrAdmin,)

    def get(self, request):
        date_from, date_to = _parse_period(request)

        rows = (
            Booking.objects.filter(start_time__date__range=(date_from, date_to))
            .exclude(status=Booking.Status.CANCELLED)
            .values('employee__id', 'employee__user__first_name', 'employee__user__last_name')
            .annotate(
                bookings_count=Count('id'),
                revenue=Sum('payment__amount', filter=Q(payment__status=Payment.Status.PAID)),
            )
            .order_by('-bookings_count')
        )

        return Response(
            {
                'date_from': date_from,
                'date_to': date_to,
                'employees': list(rows),
            }
        )


@extend_schema(tags=['reports'], parameters=PERIOD_PARAMS, responses={(200, 'text/csv'): OpenApiTypes.STR})
class BookingsCSVExportView(APIView):
    """Export bookings for a period as CSV (for accounting / offline analysis)."""

    permission_classes = (IsStaffOrAdmin,)

    def get(self, request):
        date_from, date_to = _parse_period(request)
        bookings = (
            Booking.objects.filter(start_time__date__range=(date_from, date_to))
            .select_related('client', 'employee__user', 'service')
            .order_by('start_time')
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bookings_{date_from}_{date_to}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Дата', 'Время', 'Клиент', 'Сотрудник', 'Услуга', 'Статус', 'Сумма'])
        for booking in bookings:
            payment = getattr(booking, 'payment', None)
            writer.writerow(
                [
                    booking.start_time.date().isoformat(),
                    timezone.localtime(booking.start_time).strftime('%H:%M'),
                    booking.client.get_full_name() or booking.client.username,
                    booking.employee.user.get_full_name() or booking.employee.user.username,
                    booking.service.name,
                    booking.get_status_display(),
                    payment.amount if payment else '',
                ]
            )
        return response
