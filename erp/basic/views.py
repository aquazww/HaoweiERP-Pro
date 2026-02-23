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
    CategorySerializer, CategoryTreeSerializer, WarehouseSerializer, SupplierSerializer,
    CustomerSerializer, GoodsSerializer, GoodsWithStockSerializer,
    UnitSerializer
)
from utils.views import BaseModelViewSet
from inventory.goods_inventory_service import GoodsInventoryService
from system.permissions import ModulePermission

logger = logging.getLogger(__name__)


class UnitViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filterset_fields = ['is_active']
    search_fields = ['name']
    module_name = '计量单位'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['is_active', 'parent', 'level']
    search_fields = ['name', 'code']
    module_name = '商品分类'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            if parent_id == 'null' or parent_id == '0':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        return queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        root_categories = Category.objects.filter(
            parent__isnull=True, is_active=True
        ).order_by('sort_order', 'id')
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def options(self, request):
        """获取分类选项列表（用于下拉选择）"""
        categories = Category.objects.filter(is_active=True).order_by('level', 'sort_order', 'id')
        data = []
        for cat in categories:
            prefix = '　' * (cat.level - 1)
            data.append({
                'id': cat.id,
                'name': f"{prefix}{'└ ' if cat.level > 1 else ''}{cat.name}",
                'level': cat.level,
                'parent': cat.parent_id
            })
        return Response({
            'code': 200,
            'msg': 'success',
            'data': data
        })

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取指定分类的子分类"""
        category = self.get_object()
        children = category.children.all().order_by('sort_order', 'id')
        serializer = self.get_serializer(children, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def batch_update_sort(self, request):
        """批量更新排序"""
        sort_data = request.data.get('sort_list', [])
        try:
            with transaction.atomic():
                for item in sort_data:
                    category = Category.objects.filter(id=item['id']).first()
                    if category:
                        category.sort_order = item.get('sort_order', 0)
                        parent_id = item.get('parent')
                        if parent_id and parent_id != category.parent_id:
                            parent = Category.objects.filter(id=parent_id).first()
                            if parent:
                                category.parent = parent
                                category.level = parent.level + 1
                            else:
                                category.parent = None
                                category.level = 1
                        elif parent_id is None and category.parent_id is not None:
                            category.parent = None
                            category.level = 1
                        category.save()
            return Response({'code': 200, 'msg': '排序更新成功', 'data': None})
        except Exception as e:
            return Response({'code': 400, 'msg': str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新分类状态（支持联动禁用子分类）"""
        category = self.get_object()
        new_status = request.data.get('is_active')
        cascade = request.data.get('cascade', True)
        
        if new_status is None:
            return Response({
                'code': 400,
                'msg': '请提供is_active参数',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                affected_categories = [category]
                affected_ids = [category.id]
                
                if not new_status and cascade:
                    descendants = category.get_all_descendants()
                    affected_categories.extend(descendants)
                    affected_ids.extend([d.id for d in descendants])
                
                Category.objects.filter(id__in=affected_ids).update(is_active=new_status)
                
                from system.models import Log
                Log.objects.create(
                    user=request.user,
                    action='update_status',
                    module='商品分类',
                    detail=f"{'启用' if new_status else '禁用'}分类「{category.name}」" + 
                           (f"，联动更新 {len(affected_ids) - 1} 个子分类" if len(affected_ids) > 1 else ""),
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'code': 200,
                    'msg': f"状态更新成功，共影响 {len(affected_ids)} 个分类",
                    'data': {
                        'affected_count': len(affected_ids),
                        'affected_ids': affected_ids,
                        'category_name': category.name,
                        'new_status': new_status
                    }
                })
        except Exception as e:
            logger.error(f'更新分类状态失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'更新失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance_id = instance.id
            instance_name = instance.name
            
            children = instance.children.all()
            if children.exists():
                return Response({
                    'code': 400,
                    'msg': f'无法删除分类「{instance_name}」，该分类下存在 {children.count()} 个子分类',
                    'data': {
                        'suggestion': '请先删除或移动子分类后再删除该分类'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
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
    permission_classes = [IsAuthenticated, ModulePermission]
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
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']
    module_name = '供应商'


class CustomerViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']
    module_name = '客户'


class GoodsViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Goods.objects.select_related('category').all()
    serializer_class = GoodsSerializer
    filterset_fields = ['category', 'status']
    search_fields = ['code', 'name', 'spec', 'brand']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['-created_at']
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
