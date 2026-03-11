from django.contrib import admin
from .models import Payment, PaymentRecord


class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0
    readonly_fields = ['amount', 'payment_method', 'payment_date', 'remark', 'created_by', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'type', 'related_order_no', 'related_party_name', 'total_amount', 'paid_amount', 'status', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['order_no', 'related_order_no', 'related_party_name']
    inlines = [PaymentRecordInline]
    readonly_fields = ['order_no', 'paid_amount', 'status', 'created_by', 'created_at', 'confirmed_by', 'confirmed_at']


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'payment_method', 'payment_date', 'created_by', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['payment__order_no']
