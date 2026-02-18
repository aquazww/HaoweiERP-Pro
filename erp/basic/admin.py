from django.contrib import admin
from .models import Category, Warehouse, Supplier, Customer, Goods


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'balance', 'status']
    list_filter = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'balance', 'status']
    list_filter = ['status']
    search_fields = ['code', 'name', 'contact', 'phone']


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'purchase_price', 'sale_price', 'status']
    list_filter = ['category', 'status']
    search_fields = ['code', 'name', 'barcode']
