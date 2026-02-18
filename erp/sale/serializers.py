from rest_framework import serializers
from .models import SaleOrder, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    """销售明细序列化器"""
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = '__all__'


class SaleOrderSerializer(serializers.ModelSerializer):
    """销售单序列化器"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    items = SaleItemSerializer(many=True, required=False)
    
    class Meta:
        model = SaleOrder
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by']

    def create(self, validated_data):
        """创建销售单，同时处理明细"""
        items_data = validated_data.pop('items', [])
        sale_order = SaleOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            SaleItem.objects.create(order=sale_order, **item_data)
        
        return sale_order

    def update(self, instance, validated_data):
        """更新销售单，同时处理明细"""
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SaleItem.objects.create(order=instance, **item_data)
        
        return instance
