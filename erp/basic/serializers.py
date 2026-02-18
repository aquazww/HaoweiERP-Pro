from rest_framework import serializers
from .models import Category, Warehouse, Supplier, Customer, Goods


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = Category
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    class Meta:
        model = Warehouse
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    class Meta:
        model = Supplier
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    """客户序列化器"""
    class Meta:
        model = Customer
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Goods
        fields = '__all__'
