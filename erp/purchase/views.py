from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from .models import PurchaseOrder, PurchaseItem
from .serializers import (
    PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    PurchaseItemSerializer
)
from utils.views import BaseModelViewSet
from utils.order_no import generate_stock_in_no
from inventory.models import StockIn, StockInItem
from inventory.services import InventoryService
from system.permissions import ModulePermission


class PurchaseOrderViewSet(BaseModelViewSet):
    """采购订单视图集"""
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = PurchaseOrder.objects.select_related(
        'supplier', 'warehouse', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = PurchaseOrderSerializer
    read_serializer_class = PurchaseOrderSerializer
    filterset_fields = ['supplier', 'warehouse', 'status']
    search_fields = ['order_no', 'supplier__name']
    module_name = '采购订单'
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer
    
    def perform_create(self, serializer):
        """创建时设置创建人"""
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """删除采购订单（带状态检查）"""
        try:
            instance = self.get_object()
            
            if instance.status == 'completed':
                return Response({
                    'code': 400,
                    'msg': '已入库的采购单不能删除',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            if instance.status == 'partial':
                return Response({
                    'code': 400,
                    'msg': '部分入库的采购单不能删除，请先处理完入库或取消入库',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            if instance.status == 'cancelled':
                return Response({
                    'code': 400,
                    'msg': '已取消的采购单不能删除',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            order_no = instance.order_no
            
            with transaction.atomic():
                instance.items.all().delete()
                instance.delete()
            
            self.log_action(request, 'delete', f'删除采购单: {order_no}')
            
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
    
    @action(detail=False, methods=['get'], url_path='by-no/(?P<order_no>[^/.]+)')
    def by_no(self, request, order_no=None):
        """根据单号获取订单详情"""
        order = get_object_or_404(PurchaseOrder, order_no=order_no)
        serializer = self.get_serializer(order)
        return Response({
            'code': 200,
            'msg': '获取成功',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消采购订单"""
        order = self.get_object()
        
        if order.status == 'completed':
            return Response({
                'code': 400,
                'msg': '已入库的采购单不能取消',
                'data': None
            })
        
        if order.status == 'cancelled':
            return Response({
                'code': 400,
                'msg': '采购单已取消',
                'data': None
            })
        
        order.status = 'cancelled'
        order.save()
        
        self.log_action(request, 'cancel', f'取消采购单: {order.order_no}')
        
        return Response({
            'code': 200,
            'msg': '取消成功',
            'data': None
        })

    @action(detail=True, methods=['post'])
    def confirm_inbound(self, request, pk=None):
        """确认入库（一站式入库：创建入库单 + 更新库存 + 更新采购单状态）"""
        purchase_order = self.get_object()

        if purchase_order.status not in ['pending', 'partial']:
            return Response({
                'code': 400,
                'msg': '该采购单状态不允许入库，只有待入库或部分入库状态才能入库',
                'data': None
            })

        items_data = request.data.get('items', [])
        remark = request.data.get('remark', '')

        if not items_data:
            # 如果没有传明细，则默认对所有未完全入库的商品进行入库
            items_data = []
            for item in purchase_order.items.all():
                remaining = item.quantity - (item.received_quantity or 0)
                if remaining > 0:
                    items_data.append({
                        'goods': item.goods_id,
                        'quantity': remaining,
                        'price': float(item.price)
                    })

        if not items_data:
            return Response({
                'code': 400,
                'msg': '没有需要入库的商品',
                'data': None
            })

        try:
            from decimal import Decimal

            with transaction.atomic():
                total_amount = Decimal('0')
                for item_data in items_data:
                    qty = Decimal(str(item_data.get('quantity', 0)))
                    price = Decimal(str(item_data.get('price', 0)))
                    total_amount += qty * price

                stock_in = StockIn.objects.create(
                    order_no=generate_stock_in_no(),
                    purchase_order=purchase_order,
                    warehouse=purchase_order.warehouse,
                    total_amount=total_amount,
                    status='confirmed',
                    remark=remark,
                    created_by=request.user,
                    confirmed_at=timezone.now()
                )

                for item_data in items_data:
                    goods_id = item_data.get('goods')
                    quantity = Decimal(str(item_data.get('quantity', 0)))
                    price = Decimal(str(item_data.get('price', 0)))

                    if quantity > 0:
                        from basic.models import Goods
                        goods = Goods.objects.get(id=goods_id)

                        InventoryService.stock_in(
                            goods=goods,
                            warehouse=purchase_order.warehouse,
                            quantity=int(quantity),
                            related_order=stock_in,
                            remark=f'采购入库 - {purchase_order.order_no}',
                            created_by=request.user
                        )

                        StockInItem.objects.create(
                            stock_in=stock_in,
                            goods=goods,
                            quantity=int(quantity),
                            price=price,
                            amount=quantity * price
                        )

                        purchase_item = purchase_order.items.filter(goods_id=goods_id).first()
                        if purchase_item:
                            purchase_item.received_quantity = (purchase_item.received_quantity or 0) + int(quantity)
                            purchase_item.save()

                all_received = not PurchaseItem.objects.filter(
                    order=purchase_order
                ).exclude(
                    received_quantity__gte=models.F('quantity')
                ).exists()

                if all_received:
                    purchase_order.status = 'completed'
                else:
                    purchase_order.status = 'partial'
                purchase_order.save()

                self.log_action(request, 'confirm_inbound', f'确认入库采购单: {purchase_order.order_no}')

                return Response({
                    'code': 200,
                    'msg': '入库成功',
                    'data': {
                        'stock_in_id': stock_in.id,
                        'stock_in_no': stock_in.order_no,
                        'purchase_order_status': purchase_order.status
                    }
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


class PurchaseItemViewSet(BaseModelViewSet):
    """采购明细视图集"""
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = PurchaseItem.objects.select_related('order', 'goods').all()
    serializer_class = PurchaseItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '采购订单'
