from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleOrderViewSet, SaleItemViewSet

router = DefaultRouter()
router.register(r'orders', SaleOrderViewSet)
router.register(r'items', SaleItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
