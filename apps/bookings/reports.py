from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsStaffOrAdmin

from .models import Booking, Payment


def _parse_period(request):
    """Return (date_from, date_to) parsed from query params, defaulting to the current month."""
    today = timezone.localdate()
    date_from = parse_date(request.query_params.get('date_from', '')) or today.replace(day=1)
    date_to = parse_date(request.query_params.get('date_to', '')) or today
    return date_from, date_to


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
