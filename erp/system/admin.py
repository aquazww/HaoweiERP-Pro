from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Log


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['username', 'phone', 'name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('name', 'phone', 'avatar', 'permissions')}),
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'module', 'ip_address', 'created_at']
    list_filter = ['action', 'module', 'created_at']
    search_fields = ['user__username', 'detail']
    readonly_fields = ['created_at']
