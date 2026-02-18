from django.contrib import admin
from .models import Inventory, InventoryLog, StockIn, StockOut


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['goods', 'warehouse', 'quantity', 'updated_at']
    list_filter = ['warehouse']
    search_fields = ['goods__name', 'goods__code']


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['goods', 'warehouse', 'change_type', 'change_quantity', 'created_at']
    list_filter = ['change_type', 'warehouse', 'created_at']
    search_fields = ['goods__name']
    readonly_fields = ['created_at']


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'purchase_order', 'warehouse', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_no']


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'sale_order', 'warehouse', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_no']
