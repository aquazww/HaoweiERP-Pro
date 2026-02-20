from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from decimal import Decimal

from .models import Category, Warehouse, Supplier, Customer, Goods
from .serializers import (
    CategorySerializer, WarehouseSerializer, SupplierSerializer,
    CustomerSerializer, GoodsSerializer, GoodsWithStockSerializer
)
from utils.views import BaseModelViewSet
from inventory.goods_inventory_service import GoodsInventoryService


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
    queryset = Goods.objects.select_related('category').all()
    serializer_class = GoodsSerializer
    filterset_fields = ['category', 'status']
    search_fields = ['code', 'name', 'barcode']
    module_name = '商品'

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return GoodsWithStockSerializer
        return GoodsSerializer

    def perform_create(self, serializer):
        """商品创建时初始化库存"""
        goods = serializer.save()
        GoodsInventoryService.on_goods_created(goods)

    def perform_update(self, serializer):
        """商品更新时处理状态变更"""
        instance = self.get_object()
        old_status = instance.status
        old_min_stock = instance.min_stock
        old_max_stock = instance.max_stock
        
        goods = serializer.save()
        
        if old_status != goods.status:
            GoodsInventoryService.on_goods_status_changed(goods, old_status, goods.status)
        
        if old_min_stock != goods.min_stock or old_max_stock != goods.max_stock:
            GoodsInventoryService.on_goods_stock_threshold_changed(
                goods, old_min_stock, old_max_stock
            )

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """获取商品库存信息"""
        goods = self.get_object()
        stock_status = GoodsInventoryService.get_goods_stock_status(goods)
        inventory_detail = GoodsInventoryService.get_goods_inventory_detail(goods)
        
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'goods_id': goods.id,
                'goods_code': goods.code,
                'goods_name': goods.name,
                'stock_status': stock_status,
                'inventory_detail': inventory_detail
            }
        })

    @action(detail=False, methods=['get'])
    def stock_summary(self, request):
        """获取商品库存汇总"""
        summary = GoodsInventoryService.get_goods_stock_summary()
        
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': summary
        })

    @action(detail=False, methods=['get'])
    def stock_warning(self, request):
        """获取库存预警商品"""
        warnings = GoodsInventoryService.get_stock_warning_goods()
        
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': warnings
        })

    @action(detail=False, methods=['post'])
    def check_consistency(self, request):
        """数据一致性校验"""
        goods_id = request.data.get('goods_id')
        inconsistencies = GoodsInventoryService.check_consistency(goods_id)
        
        return Response({
            'code': 200,
            'msg': '校验完成',
            'data': {
                'has_inconsistency': len(inconsistencies) > 0,
                'inconsistency_count': len(inconsistencies),
                'inconsistencies': inconsistencies
            }
        })

    @action(detail=False, methods=['post'])
    def fix_consistency(self, request):
        """修复数据不一致"""
        inconsistencies = request.data.get('inconsistencies', [])
        
        if not inconsistencies:
            return Response({
                'code': 400,
                'msg': '请提供需要修复的不一致数据',
                'data': None
            })
        
        results = []
        for item in inconsistencies:
            result = GoodsInventoryService.fix_inconsistency(item)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success'))
        
        return Response({
            'code': 200,
            'msg': f'修复完成，成功{success_count}条',
            'data': results
        })
