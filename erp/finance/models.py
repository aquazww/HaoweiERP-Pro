from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """收付款记录表"""
    TYPE_CHOICES = [
        ('receive', '收款'),
        ('pay', '付款'),
    ]

    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='单据编号')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='类型')
    related_party_type = models.CharField(max_length=50, verbose_name='往来单位类型')
    related_party_id = models.IntegerField(verbose_name='往来单位ID')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='金额')
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='付款方式')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')

    class Meta:
        db_table = 'biz_payment'
        verbose_name = '收付款记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.get_type_display()} - {self.amount}'
