from django.db import models
from django.utils import timezone


class Unit(models.Model):
    """计量单位表"""
    name = models.CharField(max_length=50, unique=True, verbose_name='单位名称')
    symbol = models.CharField(max_length=10, blank=True, verbose_name='单位符号')
    base_unit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='derived_units', verbose_name='基准单位')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True,
                                            verbose_name='换算系数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='units', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_unit'
        verbose_name = '计量单位'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """商品分类表"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    code = models.CharField(max_length=50, blank=True, verbose_name='分类编码')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='children', verbose_name='父分类')
    level = models.IntegerField(default=1, verbose_name='层级深度')
    path = models.CharField(max_length=500, blank=True, verbose_name='分类路径')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.CharField(max_length=200, blank=True, verbose_name='备注')
    created_by = models.ForeignKey('system.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='categories', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'biz_category'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['level']),
            models.Index(fields=['path']),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
            self.path = f"{self.parent.path}/{self.id}" if self.parent.path else str(self.parent.id)
        else:
            self.level = 1
            self.path = ''
        super().save(*args, **kwargs)
        
        if self.path and not self.path.endswith(str(self.id)):
            if self.parent:
                self.path = f"{self.parent.path}/{self.id}" if self.parent.path else str(self.id)
            else:
                self.path = str(self.id)
            super().save(update_fields=['path'])
    
    def get_full_path(self):
        """获取完整分类路径名称"""
        if not self.path:
            return self.name
        path_ids = [int(id) for id in self.path.split('/') if id]
        path_ids.append(self.id)
        categories = Category.objects.filter(id__in=path_ids).order_by('level')
        return ' > '.join([c.name for c in categories])
    
    def get_children_count(self):
        """获取直接子分类数量"""
        return self.children.count()
    
    def get_all_children_ids(self):
        """获取所有子分类ID列表（递归）"""
        children_ids = list(self.children.values_list('id', flat=True))
        for child in self.children.all():
            children_ids.extend(child.get_all_children_ids())
        return children_ids
    
    def get_all_descendants(self):
        """获取所有子孙分类对象（递归）"""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_all_descendants())
        return descendants


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
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True, verbose_name='计量单位')
    unit_name = models.CharField(max_length=20, blank=True, verbose_name='计量单位名称(冗余)')
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
    
    def save(self, *args, **kwargs):
        if self.unit:
            self.unit_name = self.unit.name
        super().save(*args, **kwargs)
