from django.db import models
from django.utils import timezone
from basic.models import Supplier, Goods, Warehouse


class PurchaseOrder(models.Model):
    """采购主单"""
    STATUS_CHOICES = [
        ('pending', '待入库'),
        ('partial', '部分入库'),
        ('completed', '已入库'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='采购单号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='入库仓库')
    order_date = models.DateField(default=timezone.now, verbose_name='采购日期')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='已付金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, 
                                   related_name='created_purchase_orders', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_purchase_order'
        verbose_name = '采购单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no


class PurchaseItem(models.Model):
    """采购明细"""
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购单')
    goods = models.ForeignKey(Goods, on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='数量')
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已入库数量')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='单价')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    remark = models.CharField(max_length=200, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'biz_purchase_item'
        verbose_name = '采购明细'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'goods'],
                name='unique_purchase_item_goods'
            )
        ]

    def __str__(self):
        return f'{self.order.order_no} - {self.goods.name}'
    
    def save(self, *args, **kwargs):
        """保存时自动计算金额"""
        if self.quantity and self.price:
            self.amount = self.quantity * self.price
        super().save(*args, **kwargs)
