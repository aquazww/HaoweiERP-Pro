from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Inventory, InventoryLog, StockIn, StockOut
from .serializers import (
    InventorySerializer, InventoryLogSerializer,
    StockInSerializer, StockOutSerializer
)
from .services import InventoryService
from utils.views import BaseModelViewSet
from utils.models import generate_order_no


class InventoryViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Inventory.objects.select_related('goods', 'warehouse').all()
    serializer_class = InventorySerializer
    filterset_fields = ['goods', 'warehouse']
    search_fields = ['goods__name', 'goods__code']
    module_name = '库存'


class InventoryLogViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = InventoryLog.objects.select_related('goods', 'warehouse').order_by('-created_at')
    serializer_class = InventoryLogSerializer
    filterset_fields = ['goods', 'warehouse', 'change_type']
    search_fields = ['goods__name']
    module_name = '库存流水'


class StockInViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockIn.objects.select_related(
        'warehouse', 'purchase_order', 'created_by'
    ).all()
    serializer_class = StockInSerializer
    filterset_fields = ['warehouse', 'purchase_order', 'status']
    search_fields = ['order_no']
    module_name = '入库单'

    def perform_create(self, serializer):
        """创建入库单时自动生成订单号"""
        order_no = generate_order_no(prefix='SI')
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认入库"""
        stock_in = self.get_object()
        if stock_in.status != 'pending':
            return Response({
                'code': 400,
                'msg': '该入库单状态不允许确认',
                'data': None
            })
        
        try:
            with transaction.atomic():
                # 处理采购订单明细入库
                if stock_in.purchase_order:
                    for item in stock_in.purchase_order.items.all():
                        # 计算本次入库数量（待入库数量）
                        received_qty = item.quantity - item.received_quantity
                        if received_qty > 0:
                            # 执行入库
                            InventoryService.stock_in(
                                goods=item.goods,
                                warehouse=stock_in.warehouse,
                                quantity=received_qty,
                                related_order=stock_in,
                                remark=f'采购入库，单号：{stock_in.purchase_order.order_no}'
                            )
                            # 更新采购明细的已入库数量
                            item.received_quantity = item.quantity
                            item.save()
                
                # 更新采购订单状态
                if stock_in.purchase_order:
                    purchase_order = stock_in.purchase_order
                    all_received = all(
                        item.received_quantity >= item.quantity 
                        for item in purchase_order.items.all()
                    )
                    if all_received:
                        purchase_order.status = 'completed'
                    else:
                        purchase_order.status = 'partial'
                    purchase_order.save()
                
                # 更新入库单状态
                stock_in.status = 'completed'
                stock_in.save()
                
                return Response({
                    'code': 200,
                    'msg': '入库成功',
                    'data': None
                })
        except Exception as e:
            return Response({
                'code': 400,
                'msg': str(e),
                'data': None
            })


class StockOutViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockOut.objects.select_related(
        'warehouse', 'sale_order', 'created_by'
    ).all()
    serializer_class = StockOutSerializer
    filterset_fields = ['warehouse', 'sale_order', 'status']
    search_fields = ['order_no']
    module_name = '出库单'

    def perform_create(self, serializer):
        """创建出库单时自动生成订单号"""
        order_no = generate_order_no(prefix='SO')
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )
