from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, WarehouseViewSet, SupplierViewSet,
    CustomerViewSet, GoodsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'goods', GoodsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
