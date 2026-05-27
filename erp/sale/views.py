from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from .models import SaleOrder, SaleItem
from .serializers import (
    SaleOrderSerializer, SaleOrderCreateSerializer, 
    SaleItemSerializer
)
from utils.views import BaseModelViewSet
from utils.order_no import generate_sale_order_no, generate_stock_out_no
from inventory.services import InventoryService
from inventory.models import Inventory, StockOut, StockOutItem
from system.permissions import ModulePermission
from django.utils import timezone


class SaleOrderViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = SaleOrder.objects.select_related(
        'customer', 'warehouse', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = SaleOrderSerializer
    filterset_fields = ['customer', 'warehouse', 'status']
    search_fields = ['order_no']
    module_name = '销售订单'

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return SaleOrderCreateSerializer
        return SaleOrderSerializer

    def perform_create(self, serializer):
        """创建销售单时设置创建人"""
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """删除销售单（带状态检查）"""
        try:
            instance = self.get_object()
            
            if instance.status == 'completed':
                return Response({
                    'code': 400,
                    'msg': '已出库的销售单不能删除',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            if instance.status == 'partial':
                return Response({
                    'code': 400,
                    'msg': '部分出库的销售单不能删除，请先处理完出库',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            if instance.status == 'cancelled':
                return Response({
                    'code': 400,
                    'msg': '已取消的销售单不能删除',
                    'data': None
                }, status=http_status.HTTP_400_BAD_REQUEST)
            
            order_no = instance.order_no
            
            with transaction.atomic():
                instance.items.all().delete()
                self.perform_destroy(instance)
            
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
        order = get_object_or_404(SaleOrder, order_no=order_no)
        serializer = self.get_serializer(order)
        return Response({
            'code': 200,
            'msg': '获取成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消销售订单"""
        order = self.get_object()

        if order.status == 'completed':
            return Response({
                'code': 400,
                'msg': '已出库的销售单不能取消',
                'data': None
            })

        if order.status == 'cancelled':
            return Response({
                'code': 400,
                'msg': '销售单已取消',
                'data': None
            })

        order.status = 'cancelled'
        order.save()

        self.log_action(request, 'cancel', f'取消销售单: {order.order_no}')

        return Response({
            'code': 200,
            'msg': '取消成功',
            'data': None
        })

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认出库"""
        sale_order = self.get_object()
        
        if sale_order.status not in ['pending', 'partial']:
            return Response({
                'code': 400,
                'msg': '该销售单状态不允许确认，只有待出库或部分出库状态才能确认',
                'data': None
            })
        
        # 先做库存预检查（在事务外），确保错误提示友好
        warehouse = sale_order.warehouse
        for item in sale_order.items.all():
            shipped_qty = item.quantity - (item.shipped_quantity or 0)
            if shipped_qty > 0:
                try:
                    inv = Inventory.objects.get(goods=item.goods, warehouse=warehouse)
                except Inventory.DoesNotExist:
                    return Response({
                        'code': 400,
                        'msg': f'商品「{item.goods.name}」在仓库「{warehouse.name}」无库存',
                        'data': None
                    })
                if inv.quantity < shipped_qty:
                    return Response({
                        'code': 400,
                        'msg': f'商品「{item.goods.name}」库存不足，当前库存 {inv.quantity}，需要 {shipped_qty}',
                        'data': None
                    })
        
        try:
            with transaction.atomic():
                stock_out = StockOut.objects.create(
                    order_no=generate_stock_out_no(),
                    sale_order=sale_order,
                    warehouse=warehouse,
                    total_amount=0,
                    status='confirmed',
                    created_by=request.user,
                    confirmed_at=timezone.now()
                )
                
                total_amount = 0
                for item in sale_order.items.all():
                    shipped_qty = item.quantity - (item.shipped_quantity or 0)
                    if shipped_qty > 0:
                        InventoryService.stock_out(
                            goods=item.goods,
                            warehouse=warehouse,
                            quantity=shipped_qty,
                            related_order=sale_order,
                            remark=f'销售出库 - {sale_order.order_no}',
                            created_by=request.user
                        )
                        item.shipped_quantity = item.quantity
                        item.save()
                        
                        StockOutItem.objects.create(
                            stock_out=stock_out,
                            goods=item.goods,
                            quantity=shipped_qty,
                            price=item.price,
                            amount=shipped_qty * item.price
                        )
                        total_amount += shipped_qty * item.price
                
                stock_out.total_amount = total_amount
                stock_out.save()
                
                all_shipped = not SaleItem.objects.filter(
                    order=sale_order
                ).exclude(
                    shipped_quantity__gte=models.F('quantity')
                ).exists()
                
                if all_shipped:
                    sale_order.status = 'completed'
                else:
                    sale_order.status = 'partial'
                sale_order.save()
                
                self.log_action(request, 'confirm', f'确认出库单: {sale_order.order_no}')
                
                return Response({
                    'code': 200,
                    'msg': '出库成功',
                    'data': {'stock_out_id': stock_out.id, 'stock_out_no': stock_out.order_no}
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
                'msg': f'出库失败: {str(e)}',
                'data': None
            })


class SaleItemViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = SaleItem.objects.select_related('order', 'goods').all()
    serializer_class = SaleItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '销售订单'
