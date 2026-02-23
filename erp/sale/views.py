from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import SaleOrder, SaleItem
from .serializers import (
    SaleOrderSerializer, SaleOrderCreateSerializer, 
    SaleItemSerializer
)
from utils.views import BaseModelViewSet
from utils.order_no import generate_sale_order_no
from inventory.services import InventoryService
from system.permissions import ModulePermission


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
    def confirm(self, request, pk=None):
        """确认出库"""
        sale_order = self.get_object()
        
        if sale_order.status != 'pending':
            return Response({
                'code': 400,
                'msg': '该销售单状态不允许确认，只有待出库状态才能确认',
                'data': None
            })
        
        try:
            with transaction.atomic():
                for item in sale_order.items.all():
                    shipped_qty = item.quantity - item.shipped_quantity
                    if shipped_qty > 0:
                        InventoryService.stock_out(
                            goods=item.goods,
                            warehouse=sale_order.warehouse,
                            quantity=shipped_qty,
                            related_order=sale_order,
                            remark=f'销售出库 - {sale_order.order_no}',
                            created_by=request.user
                        )
                        item.shipped_quantity = item.quantity
                        item.save()
                
                all_shipped = all(
                    item.shipped_quantity >= item.quantity 
                    for item in sale_order.items.all()
                )
                
                if all_shipped:
                    sale_order.status = 'completed'
                else:
                    sale_order.status = 'partial'
                sale_order.save()
                
                self.log_action(request, 'confirm', f'确认出库单: {sale_order.order_no}')
                
                return Response({
                    'code': 200,
                    'msg': '出库成功',
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
                'msg': f'出库失败: {str(e)}',
                'data': None
            })


class SaleItemViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = SaleItem.objects.select_related('order', 'goods').all()
    serializer_class = SaleItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '销售订单'
