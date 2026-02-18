from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryViewSet, InventoryLogViewSet,
    StockInViewSet, StockOutViewSet
)

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)
router.register(r'logs', InventoryLogViewSet)
router.register(r'stock-in', StockInViewSet)
router.register(r'stock-out', StockOutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
