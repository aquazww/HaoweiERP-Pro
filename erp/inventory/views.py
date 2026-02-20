from django.db import transaction, models
from django.db.models import Q, Sum, Count
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Inventory, InventoryLog, StockIn, StockOut, StockAdjust, StockAdjustItem, StockTransfer, StockTransferItem
from .serializers import (
    InventorySerializer, InventoryListSerializer, InventoryLogSerializer,
    StockInSerializer, StockInCreateSerializer, StockOutSerializer,
    StockAdjustSerializer, StockAdjustCreateSerializer,
    StockTransferSerializer, StockTransferCreateSerializer
)
from .services import InventoryService
from utils.views import BaseModelViewSet
from utils.order_no import generate_order_no


class InventoryViewSet(BaseModelViewSet):
    """库存视图集"""
    permission_classes = [IsAuthenticated]
    queryset = Inventory.objects.select_related(
        'goods', 'goods__category', 'warehouse'
    ).all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['warehouse', 'goods']
    search_fields = ['goods__name', 'goods__code']
    ordering_fields = ['quantity', 'updated_at', 'goods__name', 'goods__code']
    ordering = ['-updated_at']
    module_name = '库存'

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return InventoryListSerializer
        return InventorySerializer

    def get_queryset(self):
        """优化查询，支持多维度筛选"""
        queryset = super().get_queryset()
        
        params = self.request.query_params
        
        category_id = params.get('category')
        if category_id:
            queryset = queryset.filter(goods__category_id=category_id)
        
        stock_status = params.get('stock_status')
        if stock_status:
            if stock_status == 'out':
                queryset = queryset.filter(quantity__lte=0)
            elif stock_status == 'low':
                queryset = queryset.filter(
                    quantity__gt=0
                ).extra(
                    where=['quantity <= (SELECT min_stock FROM biz_goods WHERE biz_goods.id = biz_inventory.goods_id AND min_stock > 0)']
                )
            elif stock_status == 'over':
                queryset = queryset.filter(
                    quantity__gt=0
                ).extra(
                    where=['quantity >= (SELECT max_stock FROM biz_goods WHERE biz_goods.id = biz_inventory.goods_id AND max_stock > 0)']
                )
            elif stock_status == 'normal':
                queryset = queryset.filter(quantity__gt=0)
        
        quantity_min = params.get('quantity_min')
        if quantity_min:
            try:
                queryset = queryset.filter(quantity__gte=float(quantity_min))
            except (ValueError, TypeError):
                pass
        
        quantity_max = params.get('quantity_max')
        if quantity_max:
            try:
                queryset = queryset.filter(quantity__lte=float(quantity_max))
            except (ValueError, TypeError):
                pass
        
        return queryset

    def list(self, request, *args, **kwargs):
        """列表查询，包含统计信息"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                
                stats = queryset.aggregate(
                    total_quantity=Sum('quantity'),
                    total_items=Count('id'),
                    out_of_stock=Count('id', filter=Q(quantity__lte=0))
                )
                
                response = self.get_paginated_response(serializer.data)
                response.data['stats'] = {
                    'total_quantity': stats['total_quantity'] or 0,
                    'total_items': stats['total_items'] or 0,
                    'out_of_stock': stats['out_of_stock'] or 0
                }
                return response
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'code': 200,
                'msg': '查询成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': None
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除库存记录（仅管理员）"""
        try:
            if request.user.username != 'admin' and request.user.role_name != 'admin' and request.user.role_name != '管理员':
                return Response({
                    'code': 403,
                    'msg': '权限不足，只有管理员才能删除库存记录',
                    'data': None
                }, status=http_status.HTTP_403_FORBIDDEN)
            
            instance = self.get_object()
            goods_name = instance.goods.name if instance.goods else '未知商品'
            warehouse_name = instance.warehouse.name if instance.warehouse else '未知仓库'
            quantity = instance.quantity
            
            if quantity != 0:
                return Response({
                    'code': 400,
                    'msg': f'无法删除库存记录，该记录库存数量为 {quantity}，仅允许删除库存为0的记录',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            self.log_action(request, 'delete', f'删除库存记录: {goods_name} - {warehouse_name}')
            
            return Response({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'删除失败: {str(e)}',
                'data': None
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """库存汇总统计"""
        try:
            queryset = self.get_queryset()
            
            total_stats = queryset.aggregate(
                total_quantity=Sum('quantity'),
                total_items=Count('id'),
                out_of_stock=Count('id', filter=Q(quantity__lte=0))
            )
            
            warehouse_stats = queryset.values(
                'warehouse__id', 'warehouse__name'
            ).annotate(
                quantity=Sum('quantity'),
                items=Count('id')
            ).order_by('warehouse__name')
            
            category_stats = queryset.values(
                'goods__category__id', 'goods__category__name'
            ).annotate(
                quantity=Sum('quantity'),
                items=Count('id')
            ).order_by('goods__category__name')
            
            return Response({
                'code': 200,
                'msg': '查询成功',
                'data': {
                    'total': {
                        'quantity': total_stats['total_quantity'] or 0,
                        'items': total_stats['total_items'] or 0,
                        'out_of_stock': total_stats['out_of_stock'] or 0
                    },
                    'by_warehouse': list(warehouse_stats),
                    'by_category': list(category_stats)
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': None
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def warning(self, request):
        """库存预警列表"""
        try:
            queryset = self.get_queryset()
            
            warning_items = []
            for item in queryset:
                quantity = item.quantity or 0
                min_stock = item.goods.min_stock if item.goods else 0
                max_stock = item.goods.max_stock if item.goods else 0
                
                if quantity <= 0:
                    warning_items.append({
                        'id': item.id,
                        'goods_name': item.goods.name if item.goods else '',
                        'goods_code': item.goods.code if item.goods else '',
                        'warehouse_name': item.warehouse.name if item.warehouse else '',
                        'quantity': quantity,
                        'warning_type': 'out',
                        'warning_text': '缺货'
                    })
                elif min_stock > 0 and quantity <= min_stock:
                    warning_items.append({
                        'id': item.id,
                        'goods_name': item.goods.name if item.goods else '',
                        'goods_code': item.goods.code if item.goods else '',
                        'warehouse_name': item.warehouse.name if item.warehouse else '',
                        'quantity': quantity,
                        'min_stock': min_stock,
                        'warning_type': 'low',
                        'warning_text': f'库存不足(安全库存: {min_stock})'
                    })
                elif max_stock > 0 and quantity >= max_stock:
                    warning_items.append({
                        'id': item.id,
                        'goods_name': item.goods.name if item.goods else '',
                        'goods_code': item.goods.code if item.goods else '',
                        'warehouse_name': item.warehouse.name if item.warehouse else '',
                        'quantity': quantity,
                        'max_stock': max_stock,
                        'warning_type': 'over',
                        'warning_text': f'库存过剩(上限: {max_stock})'
                    })
            
            return Response({
                'code': 200,
                'msg': '查询成功',
                'data': warning_items
            })
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': None
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventoryLogViewSet(BaseModelViewSet):
    """库存流水视图集"""
    permission_classes = [IsAuthenticated]
    queryset = InventoryLog.objects.select_related(
        'goods', 'warehouse', 'created_by'
    ).order_by('-created_at')
    serializer_class = InventoryLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['warehouse', 'goods', 'change_type']
    search_fields = ['goods__name', 'goods__code']
    ordering_fields = ['created_at', 'change_quantity']
    ordering = ['-created_at']
    module_name = '库存流水'

    def get_queryset(self):
        """支持日期范围筛选"""
        queryset = super().get_queryset()
        
        params = self.request.query_params
        
        start_date = params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        end_date = params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        related_order_type = params.get('related_order_type')
        if related_order_type:
            queryset = queryset.filter(related_order_type=related_order_type)
        
        return queryset


class StockInViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockIn.objects.select_related(
        'warehouse', 'purchase_order', 'created_by'
    ).all()
    serializer_class = StockInSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['warehouse', 'purchase_order', 'status']
    search_fields = ['order_no']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    module_name = '入库单'

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return StockInCreateSerializer
        return StockInSerializer

    def perform_create(self, serializer):
        """创建入库单时自动生成订单号"""
        from utils.order_no import generate_stock_in_no
        order_no = generate_stock_in_no()
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认入库"""
        stock_in = self.get_object()
        
        if stock_in.status != 'draft':
            return Response({
                'code': 400,
                'msg': '该入库单状态不允许确认，只有草稿状态才能确认',
                'data': None
            })
        
        if not stock_in.purchase_order:
            return Response({
                'code': 400,
                'msg': '该入库单未关联采购订单',
                'data': None
            })
        
        try:
            with transaction.atomic():
                purchase_order = stock_in.purchase_order
                
                for item in purchase_order.items.all():
                    received_qty = item.quantity - item.received_quantity
                    if received_qty > 0:
                        InventoryService.stock_in(
                            goods=item.goods,
                            warehouse=stock_in.warehouse,
                            quantity=received_qty,
                            related_order=stock_in,
                            remark=f'采购入库，单号：{purchase_order.order_no}',
                            created_by=request.user
                        )
                        item.received_quantity = item.quantity
                        item.save()
                
                all_received = all(
                    item.received_quantity >= item.quantity 
                    for item in purchase_order.items.all()
                )
                
                if all_received:
                    purchase_order.status = 'completed'
                else:
                    purchase_order.status = 'partial'
                purchase_order.save()
                
                stock_in.status = 'confirmed'
                stock_in.save()
                
                self.log_action(request, 'confirm', f'确认入库单: {stock_in.order_no}')
                
                return Response({
                    'code': 200,
                    'msg': '入库成功',
                    'data': None
                })
        except ValueError as e:
            return Response({
                'code': 400,
                'msg': str(e),
                'data': None
            })
        except Exception as e:
            return Response({
                'code': 500,
                'msg': f'入库失败: {str(e)}',
                'data': None
            })


class StockOutViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockOut.objects.select_related(
        'warehouse', 'sale_order', 'created_by'
    ).all()
    serializer_class = StockOutSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['warehouse', 'sale_order', 'status']
    search_fields = ['order_no']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    module_name = '出库单'

    def perform_create(self, serializer):
        """创建出库单时自动生成订单号"""
        order_no = generate_order_no(prefix='SO')
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )


class StockAdjustViewSet(BaseModelViewSet):
    """库存调整视图集"""
    permission_classes = [IsAuthenticated]
    queryset = StockAdjust.objects.select_related('warehouse', 'created_by').prefetch_related('items').all()
    serializer_class = StockAdjustSerializer
    read_serializer_class = StockAdjustSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['warehouse', 'status', 'adjust_type', 'reason']
    search_fields = ['order_no']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    module_name = '库存调整'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StockAdjustCreateSerializer
        return StockAdjustSerializer

    def perform_create(self, serializer):
        from utils.order_no import generate_stock_adjust_no
        order_no = generate_stock_adjust_no()
        adjust = serializer.save(order_no=order_no, created_by=self.request.user)
        
        items_data = serializer.validated_data.get('items', [])
        for item_data in items_data:
            goods = item_data['goods']
            adjust_qty = item_data['adjust_quantity']
            
            try:
                inv = Inventory.objects.get(goods=goods, warehouse=adjust.warehouse)
                before_qty = inv.quantity
            except Inventory.DoesNotExist:
                before_qty = 0
                inv = Inventory.objects.create(goods=goods, warehouse=adjust.warehouse, quantity=0)
            
            if adjust.adjust_type == 'increase':
                after_qty = before_qty + adjust_qty
            else:
                after_qty = before_qty - adjust_qty
                if after_qty < 0:
                    raise ValueError(f'商品 {goods.name} 库存不足，当前库存 {before_qty}，无法减少 {adjust_qty}')
            
            StockAdjustItem.objects.create(
                adjust=adjust,
                goods=goods,
                before_quantity=before_qty,
                adjust_quantity=adjust_qty if adjust.adjust_type == 'increase' else -adjust_qty,
                after_quantity=after_qty,
                remark=item_data.get('remark', '')
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认调整"""
        adjust = self.get_object()
        
        if adjust.status != 'draft':
            return Response({'code': 400, 'msg': '只有草稿状态才能确认', 'data': None})
        
        try:
            with transaction.atomic():
                for item in adjust.items.all():
                    if item.adjust_quantity > 0:
                        InventoryService.stock_in(
                            goods=item.goods,
                            warehouse=adjust.warehouse,
                            quantity=item.adjust_quantity,
                            related_order=adjust,
                            remark=f'库存调整 - {adjust.order_no}',
                            created_by=request.user
                        )
                    else:
                        InventoryService.stock_out(
                            goods=item.goods,
                            warehouse=adjust.warehouse,
                            quantity=abs(item.adjust_quantity),
                            related_order=adjust,
                            remark=f'库存调整 - {adjust.order_no}',
                            created_by=request.user
                        )
                
                adjust.status = 'confirmed'
                adjust.confirmed_at = timezone.now()
                adjust.save()
                
                return Response({'code': 200, 'msg': '确认成功', 'data': None})
        except Exception as e:
            return Response({'code': 500, 'msg': str(e), 'data': None})


class StockTransferViewSet(BaseModelViewSet):
    """库存调拨视图集"""
    permission_classes = [IsAuthenticated]
    queryset = StockTransfer.objects.select_related('from_warehouse', 'to_warehouse', 'created_by').prefetch_related('items').all()
    serializer_class = StockTransferSerializer
    read_serializer_class = StockTransferSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['from_warehouse', 'to_warehouse', 'status']
    search_fields = ['order_no']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    module_name = '库存调拨'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StockTransferCreateSerializer
        return StockTransferSerializer

    def perform_create(self, serializer):
        from utils.order_no import generate_stock_transfer_no
        order_no = generate_stock_transfer_no()
        transfer = serializer.save(order_no=order_no, created_by=self.request.user)
        
        items_data = serializer.validated_data.get('items', [])
        for item_data in items_data:
            StockTransferItem.objects.create(
                transfer=transfer,
                goods=item_data['goods'],
                quantity=item_data['quantity'],
                remark=item_data.get('remark', '')
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认调拨"""
        transfer = self.get_object()
        
        if transfer.status != 'draft':
            return Response({'code': 400, 'msg': '只有草稿状态才能确认', 'data': None})
        
        try:
            with transaction.atomic():
                for item in transfer.items.all():
                    InventoryService.stock_out(
                        goods=item.goods,
                        warehouse=transfer.from_warehouse,
                        quantity=item.quantity,
                        related_order=transfer,
                        remark=f'调拨出库 - {transfer.order_no}',
                        created_by=request.user
                    )
                    
                    InventoryService.stock_in(
                        goods=item.goods,
                        warehouse=transfer.to_warehouse,
                        quantity=item.quantity,
                        related_order=transfer,
                        remark=f'调拨入库 - {transfer.order_no}',
                        created_by=request.user
                    )
                
                transfer.status = 'confirmed'
                transfer.confirmed_at = timezone.now()
                transfer.save()
                
                return Response({'code': 200, 'msg': '确认成功', 'data': None})
        except Exception as e:
            return Response({'code': 500, 'msg': str(e), 'data': None})
