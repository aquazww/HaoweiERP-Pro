from django.db import models
from django.utils import timezone
from basic.models import Goods, Warehouse


class Inventory(models.Model):
    """当前库存表"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='库存数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_inventory'
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        unique_together = ['goods', 'warehouse']
        indexes = [
            models.Index(fields=['goods']),
            models.Index(fields=['warehouse']),
        ]

    def __str__(self):
        return f'{self.goods.name} - {self.warehouse.name}: {self.quantity}'


class InventoryLog(models.Model):
    """库存流水表"""
    CHANGE_TYPE_CHOICES = [
        ('inbound', '入库'),
        ('outbound', '出库'),
        ('adjust', '库存调整'),
        ('check', '盘点'),
    ]

    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES, verbose_name='变动类型')
    change_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='变动数量')
    before_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='变动前数量')
    after_quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='变动后数量')
    related_order_type = models.CharField(max_length=50, blank=True, verbose_name='关联单据类型')
    related_order_id = models.IntegerField(null=True, blank=True, verbose_name='关联单据ID')
    remark = models.CharField(max_length=200, blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'biz_inventory_log'
        verbose_name = '库存流水'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['goods']),
            models.Index(fields=['warehouse']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.goods.name} - {self.change_type} - {self.created_at}'


class StockIn(models.Model):
    """入库单"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='入库单号')
    purchase_order = models.ForeignKey('purchase.PurchaseOrder', on_delete=models.SET_NULL, 
                                        null=True, blank=True, verbose_name='关联采购单')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='仓库')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')

    class Meta:
        db_table = 'biz_stock_in'
        verbose_name = '入库单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no


class StockOut(models.Model):
    """出库单"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='出库单号')
    sale_order = models.ForeignKey('sale.SaleOrder', on_delete=models.SET_NULL, 
                                   null=True, blank=True, verbose_name='关联销售单')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='仓库')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')

    class Meta:
        db_table = 'biz_stock_out'
        verbose_name = '出库单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no
