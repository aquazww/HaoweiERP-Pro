from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'type', 'amount', 'status', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['order_no']
