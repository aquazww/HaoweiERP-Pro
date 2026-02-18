from rest_framework import serializers
from .models import PurchaseOrder, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    """采购明细序列化器"""
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购单序列化器"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    items = PurchaseItemSerializer(many=True, required=False)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by']

    def create(self, validated_data):
        """创建采购单，同时处理明细"""
        items_data = validated_data.pop('items', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseItem.objects.create(order=purchase_order, **item_data)
        
        return purchase_order

    def update(self, instance, validated_data):
        """更新采购单，同时处理明细"""
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseItem.objects.create(order=instance, **item_data)
        
        return instance
