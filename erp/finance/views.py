from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer
from utils.views import BaseModelViewSet
from utils.models import generate_order_no
from system.permissions import ModulePermission


class PaymentViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Payment.objects.select_related(
        'created_by'
    ).prefetch_related('related_order').all()
    serializer_class = PaymentSerializer
    filterset_fields = ['type', 'status']
    search_fields = ['order_no']
    module_name = '收付款'

    def perform_create(self, serializer):
        """创建收付款单时自动生成订单号"""
        prefix = 'PY' if serializer.validated_data.get('type') == 'payable' else 'PR'
        order_no = generate_order_no(prefix=prefix)
        serializer.save(
            order_no=order_no,
            created_by=self.request.user
        )
