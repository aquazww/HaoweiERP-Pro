from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import SaleOrder, SaleItem
from .serializers import SaleOrderSerializer, SaleItemSerializer
from utils.views import BaseModelViewSet
from utils.models import generate_order_no
from inventory.services import InventoryService


class SaleOrderViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SaleOrder.objects.select_related(
        'customer', 'warehouse', 'created_by'
    ).prefetch_related('items').all()
    serializer_class = SaleOrderSerializer
    filterset_fields = ['customer', 'warehouse', 'status']
    search_fields = ['order_no']
    module_name = '销售订单'

    def perform_create(self, serializer):
        """创建销售单时自动生成订单号"""
        order_no = generate_order_no(prefix='SO')
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认出库"""
        sale_order = self.get_object()
        if sale_order.status != 'pending':
            return Response({
                'code': 400,
                'msg': '该销售单状态不允许确认',
                'data': None
            })
        
        try:
            with transaction.atomic():
                # 处理销售订单明细出库
                for item in sale_order.items.all():
                    # 计算本次出库数量（待出库数量）
                    shipped_qty = item.quantity - item.shipped_quantity
                    if shipped_qty > 0:
                        # 执行出库
                        InventoryService.stock_out(
                            goods=item.goods,
                            warehouse=sale_order.warehouse,
                            quantity=shipped_qty,
                            related_order=sale_order,
                            remark=f'销售出库，单号：{sale_order.order_no}'
                        )
                        # 更新销售明细的已出库数量
                        item.shipped_quantity = item.quantity
                        item.save()
                
                # 更新销售订单状态
                all_shipped = all(
                    item.shipped_quantity >= item.quantity 
                    for item in sale_order.items.all()
                )
                if all_shipped:
                    sale_order.status = 'completed'
                else:
                    sale_order.status = 'partial'
                sale_order.save()
                
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
                'code': 400,
                'msg': '出库失败',
                'data': None
            })


class SaleItemViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SaleItem.objects.select_related('order', 'goods').all()
    serializer_class = SaleItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '销售明细'
