from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, ProtectedError
from django.db import transaction, IntegrityError
from decimal import Decimal
import logging

from .models import Category, Warehouse, Supplier, Customer, Goods, Unit
from .serializers import (
    CategorySerializer, WarehouseSerializer, SupplierSerializer,
    CustomerSerializer, GoodsSerializer, GoodsWithStockSerializer,
    UnitSerializer
)
from utils.views import BaseModelViewSet
from inventory.goods_inventory_service import GoodsInventoryService

logger = logging.getLogger(__name__)


class UnitViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '计量单位'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance_name = instance.name
            
            goods_list = Goods.objects.filter(unit=instance)
            if goods_list.exists():
                goods_info = [f'{g.code} - {g.name}' for g in goods_list[:5]]
                total_count = goods_list.count()
                if total_count > 5:
                    goods_info.append(f'...等共 {total_count} 个商品')
                
                return Response({
                    'code': 400,
                    'msg': f'无法删除计量单位「{instance_name}」，该单位已被 {total_count} 个商品使用',
                    'data': {
                        'goods_list': goods_info,
                        'total_count': total_count,
                        'suggestion': '请先将这些商品的计量单位修改为其他单位，或删除这些商品后再尝试删除该计量单位'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            self.log_action(request, 'delete', f'删除计量单位: {instance_name}')
            return Response({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        except Exception as e:
            logger.error(f'删除计量单位失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'删除失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '商品分类'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance_id = instance.id
            instance_name = instance.name
            
            goods_list = Goods.objects.filter(category=instance)
            if goods_list.exists():
                goods_info = [f'{g.code} - {g.name}' for g in goods_list[:5]]
                total_count = goods_list.count()
                if total_count > 5:
                    goods_info.append(f'...等共 {total_count} 个商品')
                
                return Response({
                    'code': 400,
                    'msg': f'无法删除分类「{instance_name}」，该分类下存在 {total_count} 个关联商品',
                    'data': {
                        'goods_list': goods_info,
                        'total_count': total_count,
                        'suggestion': '请先将这些商品修改为其他分类，或删除这些商品后再尝试删除该分类'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            self.log_action(request, 'delete', f'删除分类: {instance_name}')
            return Response({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        except ProtectedError as e:
            logger.error(f'删除分类失败(保护约束): {str(e)}')
            return Response({
                'code': 400,
                'msg': '该分类下存在关联数据，无法删除',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'删除分类失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'删除失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WarehouseViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '仓库'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance_name = instance.name
            
            from inventory.models import Inventory
            inventory_list = Inventory.objects.filter(warehouse=instance)
            if inventory_list.exists():
                inventory_info = []
                total_count = 0
                for inv in inventory_list[:5]:
                    if inv.goods:
                        inventory_info.append(f'{inv.goods.code} - {inv.goods.name}（库存：{inv.quantity}）')
                        total_count += 1
                total_count = inventory_list.count()
                if total_count > 5:
                    inventory_info.append(f'...等共 {total_count} 条库存记录')
                
                return Response({
                    'code': 400,
                    'msg': f'无法删除仓库「{instance_name}」，该仓库存在 {total_count} 条库存记录',
                    'data': {
                        'goods_list': inventory_info,
                        'total_count': total_count,
                        'suggestion': '请先将该仓库的库存调拨到其他仓库，或清空库存后再尝试删除该仓库'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            self.log_action(request, 'delete', f'删除仓库: {instance_name}')
            return Response({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        except Exception as e:
            logger.error(f'删除仓库失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'删除失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        """商品创建"""
        goods = serializer.save()

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
