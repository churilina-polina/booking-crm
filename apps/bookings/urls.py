from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, PaymentViewSet

router = DefaultRouter()
router.register('bookings', BookingViewSet, basename='booking')
router.register('payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls
