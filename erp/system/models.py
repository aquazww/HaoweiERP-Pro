from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    permissions = models.JSONField(default=dict, verbose_name='权限列表')
    description = models.CharField(max_length=200, blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户表（扩展 Django 默认 User）"""
    name = models.CharField(max_length=50, blank=True, verbose_name='姓名')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='角色')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.username


class Log(models.Model):
    """操作日志表"""
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    module = models.CharField(max_length=50, verbose_name='操作模块')
    detail = models.TextField(verbose_name='操作详情')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP 地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'sys_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} - {self.created_at}'
