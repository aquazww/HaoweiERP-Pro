from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PurchaseOrder, PurchaseItem
from .serializers import PurchaseOrderSerializer, PurchaseItemSerializer
from utils.views import BaseModelViewSet
from utils.models import generate_order_no


class PurchaseOrderViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseOrder.objects.select_related('supplier', 'warehouse', 'created_by').prefetch_related('items').all()
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['supplier', 'warehouse', 'status']
    search_fields = ['order_no']
    module_name = '采购订单'

    def perform_create(self, serializer):
        """创建时自动生成订单号和设置创建人"""
        order_no = generate_order_no(prefix='PO')
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )


class PurchaseItemViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseItem.objects.select_related('order', 'goods').all()
    serializer_class = PurchaseItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '采购明细'
