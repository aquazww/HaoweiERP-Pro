from rest_framework import serializers
from .models import Inventory, InventoryLog, StockIn, StockOut


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'


class InventoryLogSerializer(serializers.ModelSerializer):
    """库存流水序列化器"""
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    class Meta:
        model = InventoryLog
        fields = '__all__'


class StockInSerializer(serializers.ModelSerializer):
    """入库单序列化器"""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    purchase_order_no = serializers.CharField(source='purchase_order.order_no', read_only=True)
    
    class Meta:
        model = StockIn
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by']


class StockOutSerializer(serializers.ModelSerializer):
    """出库单序列化器"""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    sale_order_no = serializers.CharField(source='sale_order.order_no', read_only=True)
    
    class Meta:
        model = StockOut
        fields = '__all__'
        read_only_fields = ['order_no', 'created_by']
