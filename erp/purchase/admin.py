from django.contrib import admin
from .models import PurchaseOrder, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'supplier', 'warehouse', 'order_date', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_no', 'supplier__name']
    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'goods', 'quantity', 'received_quantity', 'price', 'amount']
    search_fields = ['order__order_no', 'goods__name']
