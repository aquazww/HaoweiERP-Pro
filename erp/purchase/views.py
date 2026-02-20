from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PurchaseOrder, PurchaseItem
from .serializers import (
    PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    PurchaseItemSerializer
)
from utils.views import BaseModelViewSet


class PurchaseOrderViewSet(BaseModelViewSet):
    """采购订单视图集"""
    permission_classes = [IsAuthenticated]
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


class PurchaseItemViewSet(BaseModelViewSet):
    """采购明细视图集"""
    permission_classes = [IsAuthenticated]
    queryset = PurchaseItem.objects.select_related('order', 'goods').all()
    serializer_class = PurchaseItemSerializer
    filterset_fields = ['order', 'goods']
    module_name = '采购明细'
