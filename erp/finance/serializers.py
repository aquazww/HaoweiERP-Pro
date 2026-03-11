from rest_framework import serializers
from .models import Payment, PaymentRecord


class PaymentRecordSerializer(serializers.ModelSerializer):
    """付款记录明细序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = PaymentRecord
        fields = ['id', 'amount', 'payment_method', 'payment_method_display', 'payment_date', 'remark', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """收付款单序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)
    unpaid_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    records = PaymentRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by', 'paid_amount', 'status']


class PaymentCreateSerializer(serializers.Serializer):
    """创建收付款单序列化器"""
    type = serializers.ChoiceField(choices=Payment.TYPE_CHOICES)
    related_order_type = serializers.CharField(max_length=20)
    related_order_id = serializers.IntegerField()
    remark = serializers.CharField(required=False, allow_blank=True, default='')


class PaymentPaySerializer(serializers.Serializer):
    """付款/收款操作序列化器"""
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_date = serializers.DateField()
    remark = serializers.CharField(required=False, allow_blank=True, default='')
