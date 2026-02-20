from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryViewSet, InventoryLogViewSet,
    StockInViewSet, StockOutViewSet,
    StockAdjustViewSet, StockTransferViewSet
)

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)
router.register(r'logs', InventoryLogViewSet)
router.register(r'stock-in', StockInViewSet)
router.register(r'stock-out', StockOutViewSet)
router.register(r'adjust', StockAdjustViewSet)
router.register(r'transfer', StockTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
