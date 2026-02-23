from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from .models import Category, Warehouse, Supplier, Customer, Goods, Unit


class UnitSerializer(serializers.ModelSerializer):
    """计量单位序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    goods_count = serializers.SerializerMethodField()
    base_unit_name = serializers.CharField(source='base_unit.name', read_only=True)
    conversion_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = '__all__'
        extra_kwargs = {
            'name': {
                'validators': []
            }
        }
    
    def get_goods_count(self, obj):
        """获取关联商品数量"""
        from .models import Goods
        return Goods.objects.filter(unit=obj).count()
    
    def get_conversion_display(self, obj):
        """获取换算关系显示"""
        if obj.base_unit and obj.conversion_factor:
            return f"1{obj.name} = {obj.conversion_factor}{obj.base_unit.name}"
        return '-'
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('单位名称不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('单位名称不能超过50个字符')
        
        value = value.strip()
        
        queryset = Unit.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(f'单位名称「{value}」已存在，请使用其他名称或检查现有单位列表')
        
        return value


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    level_display = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    goods_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'level', 'level_display',
                  'path', 'full_path', 'sort_order', 'is_active', 'remark', 
                  'children_count', 'goods_count', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'level', 'path', 'created_at', 'updated_at']
    
    def get_level_display(self, obj):
        """获取层级显示名称"""
        level_names = {1: '一级分类', 2: '二级分类', 3: '三级分类', 4: '四级分类', 5: '五级分类'}
        return level_names.get(obj.level, f'{obj.level}级分类')
    
    def get_goods_count(self, obj):
        """获取该分类下的商品数量"""
        from .models import Goods
        return Goods.objects.filter(category=obj).count()
    
    def validate_name(self, value):
        """验证分类名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('分类名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('分类名称不能超过100个字符')
        return value.strip()
    
    def validate_code(self, value):
        """验证分类编码"""
        if value:
            value = value.strip().upper()
            if len(value) > 50:
                raise serializers.ValidationError('分类编码不能超过50个字符')
            queryset = Category.objects.filter(code=value)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError(f'分类编码「{value}」已存在')
        return value
    
    def validate(self, data):
        """验证父分类"""
        parent = data.get('parent')
        if parent:
            if self.instance and parent.id == self.instance.id:
                raise serializers.ValidationError({
                    'parent': '父分类不能选择当前分类本身'
                })
            if self.instance:
                all_children_ids = self.instance.get_all_children_ids()
                if parent.id in all_children_ids:
                    raise serializers.ValidationError({
                        'parent': '不能选择当前分类的子分类作为父分类'
                    })
            if parent.level >= 5:
                raise serializers.ValidationError({
                    'parent': '最多支持5级分类，当前父分类已达最大层级'
                })
        return data
    
    def to_representation(self, instance):
        """添加额外字段"""
        data = super().to_representation(instance)
        data['full_path'] = instance.get_full_path()
        data['children_count'] = instance.get_children_count()
        return data


class CategoryTreeSerializer(serializers.ModelSerializer):
    """商品分类树形结构序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'parent', 'level', 'sort_order', 
                  'is_active', 'remark', 'children']
    
    def get_children(self, obj):
        """递归获取子分类"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'id')
        return CategoryTreeSerializer(children, many=True).data


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
        extra_kwargs = {
            'code': {
                'validators': []
            }
        }
    
    def validate_code(self, value):
        """验证供应商编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('供应商编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('供应商编码不能超过50个字符')
        
        value = value.strip().upper()
        
        queryset = Supplier.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(f'供应商编码「{value}」已存在，请使用其他编码')
        
        return value
    
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
        extra_kwargs = {
            'code': {
                'validators': []
            }
        }
    
    def validate_code(self, value):
        """验证客户编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('客户编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('客户编码不能超过50个字符')
        
        value = value.strip().upper()
        
        queryset = Customer.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(f'客户编码「{value}」已存在，请使用其他编码')
        
        return value
    
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
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = Goods
        fields = '__all__'
        extra_kwargs = {
            'code': {
                'validators': []
            }
        }
    
    def validate_code(self, value):
        """验证商品编码"""
        if not value or not value.strip():
            raise serializers.ValidationError('商品编码不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('商品编码不能超过50个字符')
        
        value = value.strip().upper()
        
        queryset = Goods.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(f'商品编码「{value}」已存在，请使用其他编码')
        
        return value
    
    def validate_name(self, value):
        """验证商品名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('商品名称不能为空')
        if len(value) > 100:
            raise serializers.ValidationError('商品名称不能超过100个字符')
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
    unit = serializers.IntegerField(source='unit.id', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    total_quantity = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Goods
        fields = ['id', 'code', 'name', 'category', 'category_name', 'unit', 'unit_name', 'spec',
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
