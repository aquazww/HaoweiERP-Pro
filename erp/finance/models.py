from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """收付款记录表"""
    TYPE_CHOICES = [
        ('pay', '付款'),
        ('receive', '收款'),
    ]

    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('partial', '部分付款'),
        ('paid', '已付款'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', '现金'),
        ('bank', '银行转账'),
        ('alipay', '支付宝'),
        ('wechat', '微信'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='单据编号')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='类型')
    
    related_order_type = models.CharField(max_length=20, default='', verbose_name='关联单据类型')
    related_order_id = models.IntegerField(default=0, verbose_name='关联单据ID')
    related_order_no = models.CharField(max_length=30, default='', verbose_name='关联单据编号')
    
    related_party_type = models.CharField(max_length=50, default='', verbose_name='往来单位类型')
    related_party_id = models.IntegerField(default=0, verbose_name='往来单位ID')
    related_party_name = models.CharField(max_length=100, default='', verbose_name='往来单位名称')
    
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='总金额')
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='已付金额')
    
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='付款方式')
    payment_date = models.DateField(null=True, blank=True, verbose_name='付款日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    confirmed_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_payments', verbose_name='确认人')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')

    class Meta:
        db_table = 'biz_payment'
        verbose_name = '收付款记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.get_type_display()} - {self.total_amount}'

    @property
    def unpaid_amount(self):
        """未付金额"""
        return self.total_amount - self.paid_amount


class PaymentRecord(models.Model):
    """付款记录明细"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='records', verbose_name='收付款单')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='付款金额')
    payment_method = models.CharField(max_length=50, verbose_name='付款方式')
    payment_date = models.DateField(verbose_name='付款日期')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'biz_payment_record'
        verbose_name = '付款记录明细'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payment.order_no} - {self.amount}'
