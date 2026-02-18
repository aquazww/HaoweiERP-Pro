from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, User, Log


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'phone', 'avatar')}),
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'module', 'ip_address', 'created_at']
    list_filter = ['action', 'module', 'created_at']
    search_fields = ['user__username', 'detail']
    readonly_fields = ['created_at']
