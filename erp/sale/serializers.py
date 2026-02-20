from rest_framework import serializers
from decimal import Decimal
from .models import SaleOrder, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    """销售明细序列化器"""
    goods = serializers.IntegerField(source='goods.id', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_code = serializers.CharField(source='goods.code', read_only=True)
    unit = serializers.CharField(source='goods.unit', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'goods', 'goods_name', 'goods_code', 'unit',
                  'quantity', 'shipped_quantity', 'price', 'amount', 'remark']
        read_only_fields = ['id', 'amount']


class SaleItemCreateSerializer(serializers.ModelSerializer):
    """销售明细创建序列化器"""
    goods = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    remark = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = SaleItem
        fields = ['goods', 'quantity', 'price', 'remark']


class SaleOrderSerializer(serializers.ModelSerializer):
    """销售单序列化器"""
    customer = serializers.IntegerField(source='customer.id', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    warehouse = serializers.IntegerField(source='warehouse.id', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    items = SaleItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = SaleOrder
        fields = ['id', 'order_no', 'customer', 'customer_name', 'warehouse',
                  'warehouse_name', 'order_date', 'total_amount', 'received_amount',
                  'status', 'remark', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'order_no', 'total_amount', 'received_amount',
                           'created_at', 'updated_at']


class SaleOrderCreateSerializer(serializers.ModelSerializer):
    """销售单创建序列化器"""
    items = SaleItemCreateSerializer(many=True)
    
    class Meta:
        model = SaleOrder
        fields = ['customer', 'warehouse', 'order_date', 'remark', 'items']
    
    def validate_items(self, value):
        """验证销售明细"""
        if not value or len(value) == 0:
            raise serializers.ValidationError('销售明细不能为空')
        
        goods_ids = [item['goods'] for item in value]
        if len(goods_ids) != len(set(goods_ids)):
            raise serializers.ValidationError('销售明细中存在重复商品')
        
        return value
    
    def validate(self, data):
        """验证销售单数据"""
        if not data.get('customer'):
            raise serializers.ValidationError({'customer': '请选择客户'})
        if not data.get('warehouse'):
            raise serializers.ValidationError({'warehouse': '请选择仓库'})
        if not data.get('order_date'):
            raise serializers.ValidationError({'order_date': '请选择销售日期'})
        
        return data
    
    def create(self, validated_data):
        """创建销售单，同时处理明细"""
        from basic.models import Goods
        from utils.order_no import generate_sale_order_no
        
        items_data = validated_data.pop('items', [])
        
        total_amount = Decimal('0')
        for item_data in items_data:
            quantity = item_data['quantity']
            price = item_data['price']
            total_amount += quantity * price
        
        sale_order = SaleOrder.objects.create(
            order_no=generate_sale_order_no(),
            total_amount=total_amount,
            **validated_data
        )
        
        for item_data in items_data:
            goods = Goods.objects.get(id=item_data['goods'])
            quantity = item_data['quantity']
            price = item_data['price']
            amount = quantity * price
            
            SaleItem.objects.create(
                order=sale_order,
                goods=goods,
                quantity=quantity,
                price=price,
                amount=amount,
                remark=item_data.get('remark', '')
            )
        
        return sale_order
    
    def update(self, instance, validated_data):
        """更新销售单，同时处理明细"""
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
                
                SaleItem.objects.create(
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
