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
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    permissions = models.JSONField(default=dict, blank=True, verbose_name='权限列表')
    token_version = models.IntegerField(default=0, verbose_name='Token版本号')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.username
    
    def get_permissions(self):
        """获取用户权限"""
        return self.permissions if self.permissions else {}
    
    def has_permission(self, module, action='view'):
        """检查用户是否有指定模块的权限"""
        if self.username == 'admin':
            return True
        permissions = self.get_permissions()
        module_perms = permissions.get(module, {})
        return module_perms.get(action, False) if isinstance(module_perms, dict) else module_perms
    
    def get_all_permissions(self):
        """获取用户所有权限（用于前端菜单显示）"""
        if self.username == 'admin':
            return {
                'basic': {'view': True, 'add': True, 'edit': True, 'delete': True},
                'purchase': {'view': True, 'add': True, 'edit': True, 'delete': True},
                'sale': {'view': True, 'add': True, 'edit': True, 'delete': True},
                'inventory': {'view': True, 'add': True, 'edit': True, 'delete': True},
                'finance': {'view': True, 'add': True, 'edit': True, 'delete': True},
                'reports': {'view': True},
                'system': {'view': True, 'add': True, 'edit': True, 'delete': True}
            }
        return self.get_permissions()
    
    def invalidate_tokens(self):
        """使所有token失效"""
        self.token_version += 1
        self.save(update_fields=['token_version'])


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
