from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, WarehouseViewSet, SupplierViewSet,
    CustomerViewSet, GoodsViewSet, UnitViewSet, CompanyInfoViewSet,
    PrintTemplateViewSet
)

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'goods', GoodsViewSet)
router.register(r'company', CompanyInfoViewSet, basename='company')
router.register(r'print-templates', PrintTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
