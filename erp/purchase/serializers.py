from rest_framework import serializers
from decimal import Decimal
from .models import PurchaseOrder, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    """采购明细序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    goods_spec = serializers.CharField(source='goods.spec', read_only=True)
    unit = serializers.CharField(source='goods.unit.name', read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'goods_spec', 'unit', 
                  'quantity', 'price', 'amount', 'remark']
        read_only_fields = ['id', 'amount']
    
    def validate_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError('采购数量必须大于0')
        return value
    
    def validate_price(self, value):
        """验证单价"""
        if value < 0:
            raise serializers.ValidationError('采购单价不能为负数')
        return value
    
    def validate(self, data):
        """验证明细数据"""
        quantity = data.get('quantity', Decimal('0'))
        price = data.get('price', Decimal('0'))
        
        if quantity > 0 and price <= 0:
            raise serializers.ValidationError({'price': '采购单价必须大于0'})
        
        return data


class PurchaseItemCreateSerializer(serializers.ModelSerializer):
    """采购明细创建序列化器"""
    goods = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    remark = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = PurchaseItem
        fields = ['goods', 'quantity', 'price', 'remark']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购单序列化器"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)
    stock_in_time = serializers.SerializerMethodField(read_only=True)
    stock_in_remark = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'order_no', 'supplier', 'supplier_name', 'warehouse', 
                  'warehouse_name', 'order_date', 'total_amount', 'paid_amount', 
                  'status', 'remark', 'items', 'created_by', 'created_by_name',
                  'created_at', 'updated_at', 'stock_in_time', 'stock_in_remark']
        read_only_fields = ['id', 'order_no', 'total_amount', 'paid_amount', 
                           'created_by', 'created_at', 'updated_at']
    
    def get_stock_in_time(self, obj):
        """获取入库时间"""
        from inventory.models import StockIn
        stock_in = StockIn.objects.filter(purchase_order=obj, status='confirmed').first()
        if stock_in:
            return stock_in.created_at
        return None
    
    def get_stock_in_remark(self, obj):
        """获取入库备注"""
        from inventory.models import StockIn
        stock_in = StockIn.objects.filter(purchase_order=obj, status='confirmed').first()
        if stock_in:
            return stock_in.remark
        return None
    
    def validate_status(self, value):
        """验证状态"""
        if self.instance and self.instance.status in ['completed', 'cancelled']:
            if value != self.instance.status:
                raise serializers.ValidationError('已完成或已取消的订单不能修改状态')
        return value


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """采购单创建序列化器"""
    items = PurchaseItemCreateSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'warehouse', 'order_date', 'remark', 'items']
    
    def validate_items(self, value):
        """验证采购明细"""
        if not value or len(value) == 0:
            raise serializers.ValidationError('采购明细不能为空')
        
        goods_ids = [item['goods'] for item in value]
        if len(goods_ids) != len(set(goods_ids)):
            raise serializers.ValidationError('采购明细中存在重复商品')
        
        return value
    
    def validate(self, data):
        """验证采购单数据"""
        if not data.get('supplier'):
            raise serializers.ValidationError({'supplier': '请选择供应商'})
        if not data.get('warehouse'):
            raise serializers.ValidationError({'warehouse': '请选择仓库'})
        if not data.get('order_date'):
            raise serializers.ValidationError({'order_date': '请选择采购日期'})
        
        return data
    
    def create(self, validated_data):
        """创建采购单，同时处理明细"""
        from basic.models import Goods
        from utils.order_no import generate_purchase_order_no
        
        items_data = validated_data.pop('items', [])
        
        total_amount = Decimal('0')
        for item_data in items_data:
            quantity = item_data['quantity']
            price = item_data['price']
            total_amount += quantity * price
        
        purchase_order = PurchaseOrder.objects.create(
            order_no=generate_purchase_order_no(),
            total_amount=total_amount,
            **validated_data
        )
        
        for item_data in items_data:
            goods = Goods.objects.get(id=item_data['goods'])
            quantity = item_data['quantity']
            price = item_data['price']
            amount = quantity * price
            
            PurchaseItem.objects.create(
                order=purchase_order,
                goods=goods,
                quantity=quantity,
                price=price,
                amount=amount,
                remark=item_data.get('remark', '')
            )
        
        return purchase_order
    
    def update(self, instance, validated_data):
        """更新采购单，同时处理明细"""
        from basic.models import Goods
        
        items_data = validated_data.pop('items', None)
        
        if items_data is not None:
            if instance.status in ['completed', 'cancelled']:
                raise serializers.ValidationError('已完成或已取消的订单不能修改')
            
            instance.items.all().delete()
            
            total_amount = Decimal('0')
            for item_data in items_data:
                goods = Goods.objects.get(id=item_data['goods'])
                quantity = item_data['quantity']
                price = item_data['price']
                amount = quantity * price
                total_amount += amount
                
                PurchaseItem.objects.create(
                    order=instance,
                    goods=goods,
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    remark=item_data.get('remark', '')
                )
            
            instance.total_amount = total_amount
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
