from rest_framework.permissions import IsAuthenticated
from .models import Category, Warehouse, Supplier, Customer, Goods
from .serializers import (
    CategorySerializer, WarehouseSerializer, SupplierSerializer,
    CustomerSerializer, GoodsSerializer
)
from utils.views import BaseModelViewSet


class CategoryViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '商品分类'


class WarehouseViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '仓库'


class SupplierViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']
    module_name = '供应商'


class CustomerViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']
    module_name = '客户'


class GoodsViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    filterset_fields = ['category', 'status']
    search_fields = ['code', 'name', 'barcode']
    module_name = '商品'
