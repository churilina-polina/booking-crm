from django.urls import path
from rest_framework.routers import DefaultRouter

from .reports import EmployeeLoadReportView, RevenueReportView
from .views import BookingViewSet, PaymentViewSet

router = DefaultRouter()
router.register('bookings', BookingViewSet, basename='booking')
router.register('payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls + [
    path('reports/revenue/', RevenueReportView.as_view(), name='report-revenue'),
    path('reports/employee-load/', EmployeeLoadReportView.as_view(), name='report-employee-load'),
]
