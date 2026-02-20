from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from .models import Category, Warehouse, Supplier, Customer, Goods


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def validate_name(self, value):
        """验证分类名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('分类名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('分类名称不能超过100个字符')
        return value.strip()
    
    def validate(self, data):
        """验证父分类不能是自己"""
        if data.get('parent'):
            if data['parent'].id == self.instance.id if self.instance else False:
                raise serializers.ValidationError({'parent': '父分类不能是自己'})
        return data


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    
    class Meta:
        model = Warehouse
        fields = '__all__'
    
    def validate_name(self, value):
        """验证仓库名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('仓库名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('仓库名称不能超过100个字符')
        return value.strip()
    
    def validate_phone(self, value):
        """验证联系电话"""
        if value:
            import re
            if not re.match(r'^[\d\-+()]+$', value):
                raise serializers.ValidationError('请输入有效的电话号码')
        return value


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    
    class Meta:
        model = Supplier
        fields = '__all__'
    
    def validate_code(self, value):
        """验证供应商编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('供应商编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('供应商编码不能超过50个字符')
        return value.strip().upper()
    
    def validate_name(self, value):
        """验证公司名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('公司名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('公司名称不能超过100个字符')
        return value.strip()
    
    def validate_tax_no(self, value):
        """验证税号"""
        if not value or not value.strip():
            raise serializers.ValidationError('税号不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('税号不能超过50个字符')
        return value.strip()
    
    def validate_email(self, value):
        """验证邮箱"""
        if value:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError('请输入有效的邮箱地址')
        return value
    
    def validate_balance(self, value):
        """验证应付余额"""
        if value < 0:
            raise serializers.ValidationError('应付余额不能为负数')
        return value


class CustomerSerializer(serializers.ModelSerializer):
    """客户序列化器"""
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def validate_code(self, value):
        """验证客户编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('客户编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('客户编码不能超过50个字符')
        return value.strip().upper()
    
    def validate_name(self, value):
        """验证公司名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('公司名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('公司名称不能超过100个字符')
        return value.strip()
    
    def validate_tax_no(self, value):
        """验证税号"""
        if not value or not value.strip():
            raise serializers.ValidationError('税号不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('税号不能超过50个字符')
        return value.strip()
    
    def validate_email(self, value):
        """验证邮箱"""
        if value:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError('请输入有效的邮箱地址')
        return value
    
    def validate_balance(self, value):
        """验证应收余额"""
        if value < 0:
            raise serializers.ValidationError('应收余额不能为负数')
        return value


class GoodsSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Goods
        fields = '__all__'
    
    def validate_code(self, value):
        """验证商品编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('商品编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('商品编码不能超过50个字符')
        return value.strip().upper()
    
    def validate_name(self, value):
        """验证商品名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('商品名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('商品名称不能超过100个字符')
        return value.strip()
    
    def validate_unit(self, value):
        """验证计量单位"""
        if not value or not value.strip():
            raise serializers.ValidationError('计量单位不能为空')
        return value.strip()
    
    def validate_purchase_price(self, value):
        """验证进货价"""
        if value < 0:
            raise serializers.ValidationError('进货价不能为负数')
        return value
    
    def validate_sale_price(self, value):
        """验证销售价"""
        if value < 0:
            raise serializers.ValidationError('销售价不能为负数')
        return value
    
    def validate_retail_price(self, value):
        """验证零售价"""
        if value < 0:
            raise serializers.ValidationError('零售价不能为负数')
        return value
    
    def validate_min_stock(self, value):
        """验证最低库存"""
        if value < 0:
            raise serializers.ValidationError('最低库存不能为负数')
        return value
    
    def validate_max_stock(self, value):
        """验证最高库存"""
        if value < 0:
            raise serializers.ValidationError('最高库存不能为负数')
        return value
    
    def validate(self, data):
        """验证价格和库存逻辑"""
        purchase_price = data.get('purchase_price', 0)
        sale_price = data.get('sale_price', 0)
        min_stock = data.get('min_stock', 0)
        max_stock = data.get('max_stock', 0)
        
        if sale_price < purchase_price:
            raise serializers.ValidationError({'sale_price': '销售价不能低于进货价'})
        
        if max_stock < min_stock:
            raise serializers.ValidationError({'max_stock': '最高库存不能低于最低库存'})
        
        return data


class GoodsWithStockSerializer(serializers.ModelSerializer):
    """带库存信息的商品序列化器"""
    category = serializers.IntegerField(source='category.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_quantity = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Goods
        fields = ['id', 'code', 'name', 'category', 'category_name', 'unit', 'spec',
                  'barcode', 'purchase_price', 'sale_price', 'retail_price',
                  'min_stock', 'max_stock', 'status', 'total_quantity', 'stock_status',
                  'created_at', 'updated_at']
    
    def get_total_quantity(self, obj):
        """获取商品总库存"""
        from inventory.models import Inventory
        
        total = Inventory.objects.filter(goods=obj).aggregate(
            total=Sum('quantity')
        )['total']
        return total or Decimal('0')
    
    def get_stock_status(self, obj):
        """获取库存状态"""
        total_quantity = self.get_total_quantity(obj)
        min_stock = obj.min_stock or 0
        max_stock = obj.max_stock or 0
        
        if total_quantity <= 0:
            return {'code': 'out', 'text': '缺货'}
        elif min_stock > 0 and total_quantity <= min_stock:
            return {'code': 'low', 'text': '库存不足'}
        elif max_stock > 0 and total_quantity >= max_stock:
            return {'code': 'over', 'text': '库存过剩'}
        else:
            return {'code': 'normal', 'text': '正常'}
