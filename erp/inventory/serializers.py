from rest_framework import serializers
from .models import Inventory, InventoryLog, StockIn, StockOut, StockAdjust, StockAdjustItem, StockTransfer, StockTransferItem


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    category = serializers.IntegerField(source='goods.category.id', read_only=True)
    category_name = serializers.CharField(source='goods.category.name', read_only=True)
    unit = serializers.CharField(source='goods.unit.name', read_only=True)
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'category', 'category_name',
                  'unit', 'warehouse', 'warehouse_name', 'quantity', 'stock_status',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_stock_status(self, obj):
        """获取库存状态"""
        quantity = obj.quantity or 0
        min_stock = obj.goods.min_stock if obj.goods else 0
        max_stock = obj.goods.max_stock if obj.goods else 0
        
        if quantity <= 0:
            return {'code': 'out', 'text': '缺货', 'class': 'danger'}
        elif min_stock > 0 and quantity <= min_stock:
            return {'code': 'low', 'text': '库存不足', 'class': 'warning'}
        elif max_stock > 0 and quantity >= max_stock:
            return {'code': 'over', 'text': '库存过剩', 'class': 'info'}
        else:
            return {'code': 'normal', 'text': '正常', 'class': 'success'}


class InventoryListSerializer(serializers.ModelSerializer):
    """库存列表序列化器（优化查询）"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    category = serializers.IntegerField(source='goods.category.id', read_only=True)
    category_name = serializers.CharField(source='goods.category.name', read_only=True)
    unit = serializers.CharField(source='goods.unit.name', read_only=True)
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    min_stock = serializers.IntegerField(source='goods.min_stock', read_only=True)
    max_stock = serializers.IntegerField(source='goods.max_stock', read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'category', 'category_name',
                  'unit', 'warehouse', 'warehouse_name', 'quantity', 'min_stock', 'max_stock',
                  'stock_status', 'updated_at']
    
    def get_stock_status(self, obj):
        """获取库存状态"""
        quantity = obj.quantity or 0
        min_stock = obj.goods.min_stock if obj.goods else 0
        max_stock = obj.goods.max_stock if obj.goods else 0
        
        if quantity <= 0:
            return {'code': 'out', 'text': '缺货'}
        elif min_stock > 0 and quantity <= min_stock:
            return {'code': 'low', 'text': '库存不足'}
        elif max_stock > 0 and quantity >= max_stock:
            return {'code': 'over', 'text': '库存过剩'}
        else:
            return {'code': 'normal', 'text': '正常'}


class InventoryLogSerializer(serializers.ModelSerializer):
    """库存流水序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = InventoryLog
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'warehouse', 'warehouse_name',
                  'change_type', 'change_type_display', 'change_quantity',
                  'before_quantity', 'after_quantity', 'related_order_type',
                  'related_order_id', 'remark', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockInSerializer(serializers.ModelSerializer):
    """入库单序列化器"""
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    purchase_order = serializers.IntegerField(source='purchase_order.id', read_only=True)
    purchase_order_no = serializers.CharField(source='purchase_order.order_no', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StockIn
        fields = ['id', 'order_no', 'warehouse', 'warehouse_name', 'purchase_order',
                  'purchase_order_no', 'total_amount', 'status', 'status_display', 'remark',
                  'created_by', 'created_by_name', 'created_at', 'confirmed_at']
        read_only_fields = ['id', 'order_no', 'created_by', 'created_at', 'confirmed_at']


class StockInCreateSerializer(serializers.ModelSerializer):
    """入库单创建序列化器"""
    
    class Meta:
        model = StockIn
        fields = ['warehouse', 'purchase_order', 'total_amount', 'remark']


class StockOutSerializer(serializers.ModelSerializer):
    """出库单序列化器"""
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    sale_order = serializers.IntegerField(source='sale_order.id', read_only=True)
    sale_order_no = serializers.CharField(source='sale_order.order_no', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StockOut
        fields = ['id', 'order_no', 'warehouse', 'warehouse_name', 'sale_order',
                  'sale_order_no', 'total_amount', 'status', 'status_display', 'remark',
                  'created_by', 'created_by_name', 'created_at', 'confirmed_at']
        read_only_fields = ['id', 'order_no', 'created_by', 'created_at', 'confirmed_at']


class StockAdjustItemSerializer(serializers.ModelSerializer):
    """库存调整明细序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    unit = serializers.CharField(source='goods.unit.name', read_only=True)
    
    class Meta:
        model = StockAdjustItem
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'unit', 
                  'before_quantity', 'adjust_quantity', 'after_quantity', 'remark']


class StockAdjustItemCreateSerializer(serializers.ModelSerializer):
    """库存调整明细创建序列化器"""
    
    class Meta:
        model = StockAdjustItem
        fields = ['goods', 'adjust_quantity', 'remark']


class StockAdjustSerializer(serializers.ModelSerializer):
    """库存调整单序列化器"""
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    adjust_type_display = serializers.CharField(source='get_adjust_type_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    items = StockAdjustItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockAdjust
        fields = ['id', 'order_no', 'warehouse', 'warehouse_name', 'adjust_type', 'adjust_type_display',
                  'reason', 'reason_display', 'status', 'status_display', 'remark',
                  'items', 'created_by', 'created_by_name', 'created_at', 'confirmed_at']
        read_only_fields = ['id', 'order_no', 'created_by', 'created_at', 'confirmed_at']


class StockAdjustCreateSerializer(serializers.ModelSerializer):
    """库存调整单创建序列化器"""
    items = StockAdjustItemCreateSerializer(many=True)
    
    class Meta:
        model = StockAdjust
        fields = ['warehouse', 'adjust_type', 'reason', 'remark', 'items']
    
    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError('请添加调整明细')
        
        goods_ids = [item['goods'] for item in value]
        if len(goods_ids) != len(set(goods_ids)):
            raise serializers.ValidationError('调整明细中存在重复商品')
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        adjust = StockAdjust.objects.create(**validated_data)
        return adjust


class StockTransferItemSerializer(serializers.ModelSerializer):
    """库存调拨明细序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    unit = serializers.CharField(source='goods.unit.name', read_only=True)
    
    class Meta:
        model = StockTransferItem
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'unit', 'quantity', 'remark']


class StockTransferItemCreateSerializer(serializers.ModelSerializer):
    """库存调拨明细创建序列化器"""
    
    class Meta:
        model = StockTransferItem
        fields = ['goods', 'quantity', 'remark']


class StockTransferSerializer(serializers.ModelSerializer):
    """库存调拨单序列化器"""
    from_warehouse = serializers.IntegerField(source='from_warehouse.id', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse = serializers.IntegerField(source='to_warehouse.id', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    items = StockTransferItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = ['id', 'order_no', 'from_warehouse', 'from_warehouse_name', 
                  'to_warehouse', 'to_warehouse_name', 'status', 'status_display', 
                  'remark', 'items', 'created_by', 'created_by_name', 'created_at', 'confirmed_at']
        read_only_fields = ['id', 'order_no', 'created_by', 'created_at', 'confirmed_at']


class StockTransferCreateSerializer(serializers.ModelSerializer):
    """库存调拨单创建序列化器"""
    items = StockTransferItemCreateSerializer(many=True)
    
    class Meta:
        model = StockTransfer
        fields = ['from_warehouse', 'to_warehouse', 'remark', 'items']
    
    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError('请添加调拨明细')
        
        goods_ids = [item['goods'] for item in value]
        if len(goods_ids) != len(set(goods_ids)):
            raise serializers.ValidationError('调拨明细中存在重复商品')
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        transfer = StockTransfer.objects.create(**validated_data)
        return transfer
    
    def validate(self, data):
        if data.get('from_warehouse') == data.get('to_warehouse'):
            raise serializers.ValidationError({'to_warehouse': '调入仓库不能与调出仓库相同'})
        return data
