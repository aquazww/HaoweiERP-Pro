from django.db import models
from django.utils import timezone


class Category(models.Model):
    """商品分类表"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='children', verbose_name='父分类')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_category'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """仓库表"""
    name = models.CharField(max_length=100, verbose_name='仓库名称')
    address = models.CharField(max_length=200, blank=True, verbose_name='仓库地址')
    contact = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_warehouse'
        verbose_name = '仓库'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """供应商表"""
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='供应商编码')
    name = models.CharField(max_length=100, verbose_name='公司名称')
    tax_no = models.CharField(max_length=50, verbose_name='税号')
    address = models.CharField(max_length=200, verbose_name='地址')
    contact = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, verbose_name='公司邮箱')
    bank_name = models.CharField(max_length=100, blank=True, verbose_name='开户银行')
    bank_account = models.CharField(max_length=50, blank=True, verbose_name='银行账号')
    bank_branch_no = models.CharField(max_length=50, blank=True, verbose_name='支行行号')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='应付余额')
    remark = models.TextField(blank=True, verbose_name='备注信息')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_supplier'
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'


class Customer(models.Model):
    """客户表"""
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '启用'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='客户编码')
    name = models.CharField(max_length=100, verbose_name='公司名称')
    tax_no = models.CharField(max_length=50, verbose_name='税号')
    address = models.CharField(max_length=200, verbose_name='公司地址')
    contact = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, verbose_name='公司邮箱')
    bank_name = models.CharField(max_length=100, blank=True, verbose_name='开户银行')
    bank_account = models.CharField(max_length=50, blank=True, verbose_name='银行账号')
    bank_branch_no = models.CharField(max_length=50, blank=True, verbose_name='支行行号')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='应收余额')
    remark = models.TextField(blank=True, verbose_name='备注信息')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_customer'
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'


class Goods(models.Model):
    """商品表"""
    STATUS_CHOICES = [
        (0, '下架'),
        (1, '上架'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='商品编码')
    name = models.CharField(max_length=100, verbose_name='商品名称')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='商品分类')
    unit = models.CharField(max_length=20, verbose_name='计量单位')
    spec = models.CharField(max_length=100, blank=True, verbose_name='规格')
    barcode = models.CharField(max_length=50, blank=True, verbose_name='条形码')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='进货价')
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='销售价')
    retail_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='零售价')
    min_stock = models.IntegerField(default=0, verbose_name='最低库存')
    max_stock = models.IntegerField(default=0, verbose_name='最高库存')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'
