from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, ServiceViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet, basename='service')
router.register('employees', EmployeeViewSet, basename='employee')

urlpatterns = router.urls
