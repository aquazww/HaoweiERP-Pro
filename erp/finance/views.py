from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.utils.dateparse import parse_date

from .models import Payment, PaymentRecord
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentPaySerializer
from utils.views import BaseModelViewSet
from utils.models import generate_order_no
from system.permissions import ModulePermission
from purchase.models import PurchaseOrder
from sale.models import SaleOrder


class PaymentViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated, ModulePermission]
    queryset = Payment.objects.select_related('created_by', 'confirmed_by').prefetch_related('records').all()
    serializer_class = PaymentSerializer
    filterset_fields = ['type', 'status']
    search_fields = ['order_no', 'related_order_no', 'related_party_name']
    module_name = '收付款'

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """创建收付款单"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        order_type = data.get('related_order_type')
        order_id = data.get('related_order_id')
        remark = data.get('remark', '')
        
        try:
            if order_type == 'purchase':
                order = PurchaseOrder.objects.get(id=order_id)
                payment_type = 'pay'
                related_party_type = 'supplier'
                related_party_id = order.supplier_id
                related_party_name = order.supplier.name
            elif order_type == 'sale':
                order = SaleOrder.objects.get(id=order_id)
                payment_type = 'receive'
                related_party_type = 'customer'
                related_party_id = order.customer_id
                related_party_name = order.customer.name
            else:
                return Response({'code': 400, 'msg': '不支持的单据类型'}, status=400)
        except (PurchaseOrder.DoesNotExist, SaleOrder.DoesNotExist):
            return Response({'code': 404, 'msg': '关联订单不存在'}, status=404)
        
        existing_payment = Payment.objects.filter(
            related_order_type=order_type,
            related_order_id=order_id
        ).first()
        
        if existing_payment:
            payment = existing_payment
            payment.remark = remark
            payment.save()
        else:
            prefix = 'PP' if payment_type == 'pay' else 'PR'
            order_no = generate_order_no(prefix=prefix)
            payment = Payment.objects.create(
                order_no=order_no,
                type=payment_type,
                related_order_type=order_type,
                related_order_id=order_id,
                related_order_no=order.order_no,
                related_party_type=related_party_type,
                related_party_id=related_party_id,
                related_party_name=related_party_name,
                total_amount=order.total_amount,
                remark=remark,
                created_by=request.user
            )
        
        return Response({
            'code': 200,
            'msg': '创建成功',
            'data': PaymentSerializer(payment).data
        })

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def pay(self, request, pk=None):
        """付款/收款操作"""
        payment = self.get_object()
        serializer = PaymentPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        amount = data['amount']
        payment_method = data['payment_method']
        payment_date = data['payment_date']
        remark = data.get('remark', '')
        
        if amount > payment.unpaid_amount:
            return Response({
                'code': 400,
                'msg': f'付款金额不能超过未付金额 ¥{payment.unpaid_amount}'
            })
        
        payment.paid_amount += amount
        if payment.paid_amount >= payment.total_amount:
            payment.status = 'paid'
            payment.confirmed_by = request.user
            payment.confirmed_at = timezone.now()
        else:
            payment.status = 'partial'
        payment.payment_method = payment_method
        payment.payment_date = payment_date
        payment.save()
        
        PaymentRecord.objects.create(
            payment=payment,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            remark=remark,
            created_by=request.user
        )
        
        if payment.related_order_type == 'purchase':
            PurchaseOrder.objects.filter(id=payment.related_order_id).update(
                paid_amount=payment.paid_amount
            )
        elif payment.related_order_type == 'sale':
            SaleOrder.objects.filter(id=payment.related_order_id).update(
                received_amount=payment.paid_amount
            )
        
        return Response({
            'code': 200,
            'msg': '付款成功',
            'data': PaymentSerializer(payment).data
        })

    @action(detail=False, methods=['get'])
    def order_info(self, request):
        """获取订单信息"""
        order_type = request.query_params.get('order_type')
        order_id = request.query_params.get('order_id')
        
        if not order_type or not order_id:
            return Response({'code': 400, 'msg': '缺少参数'})
        
        try:
            if order_type == 'purchase':
                order = PurchaseOrder.objects.get(id=order_id)
                payment_type = 'pay'
                related_party_name = order.supplier.name
            elif order_type == 'sale':
                order = SaleOrder.objects.get(id=order_id)
                payment_type = 'receive'
                related_party_name = order.customer.name
            else:
                return Response({'code': 400, 'msg': '不支持的单据类型'})
            
            existing_payment = Payment.objects.filter(
                related_order_type=order_type,
                related_order_id=order_id
            ).first()
            
            paid_amount = existing_payment.paid_amount if existing_payment else 0
            unpaid_amount = order.total_amount - paid_amount
            
            return Response({
                'code': 200,
                'data': {
                    'order_no': order.order_no,
                    'total_amount': order.total_amount,
                    'paid_amount': paid_amount,
                    'unpaid_amount': unpaid_amount,
                    'payment_type': payment_type,
                    'related_party_name': related_party_name,
                    'status': order.status
                }
            })
        except (PurchaseOrder.DoesNotExist, SaleOrder.DoesNotExist):
            return Response({'code': 404, 'msg': '订单不存在'})
