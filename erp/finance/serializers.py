from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """收付款单序列化器"""
    related_order_no = serializers.CharField(
        source='related_order.order_no', read_only=True, allow_null=True
    )
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by']
