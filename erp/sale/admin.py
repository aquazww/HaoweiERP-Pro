from django.contrib import admin
from .models import SaleOrder, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'customer', 'warehouse', 'order_date', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_no', 'customer__name']
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'goods', 'quantity', 'shipped_quantity', 'price', 'amount']
    search_fields = ['order__order_no', 'goods__name']
