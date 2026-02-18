from django.db import models
from django.utils import timezone
from basic.models import Customer, Goods, Warehouse


class SaleOrder(models.Model):
    """销售主单"""
    STATUS_CHOICES = [
        ('pending', '待出库'),
        ('partial', '部分出库'),
        ('completed', '已出库'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='销售单号')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='客户')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='出库仓库')
    order_date = models.DateField(default=timezone.now, verbose_name='销售日期')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    received_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='已收金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, 
                                   related_name='created_sale_orders', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_sale_order'
        verbose_name = '销售单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no


class SaleItem(models.Model):
    """销售明细"""
    order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='items', verbose_name='销售单')
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='数量')
    shipped_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已出库数量')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='单价')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    remark = models.CharField(max_length=200, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'biz_sale_item'
        verbose_name = '销售明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.order.order_no} - {self.goods.name}'
