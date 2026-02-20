import logging
from rest_framework import permissions
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员角色用户访问
    管理员角色名称为: admin 或 管理员
    """
    message = '您没有权限执行此操作，请联系管理员'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            logger.warning(f'未认证用户尝试访问: {request.path}')
            return False
        
        if request.user.username == 'admin':
            return True
        
        if request.user.role and request.user.role.name in ['admin', '管理员']:
            return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试访问 {request.path}，'
            f'角色: {request.user.role.name if request.user.role else "无角色"}，权限不足'
        )
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员可以执行所有操作，其他用户只能读取
    """
    message = '您没有权限执行此操作，请联系管理员'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.username == 'admin':
            return True
        
        if request.user.role and request.user.role.name in ['admin', '管理员']:
            return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试执行 {request.method} 操作，权限不足'
        )
        return False


class IsSelfOrAdmin(permissions.BasePermission):
    """
    用户只能查看/编辑自己的信息，管理员可以操作所有用户
    """
    message = '您只能操作自己的信息'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.username == 'admin':
            return True
        
        if request.user.role and request.user.role.name in ['admin', '管理员']:
            return True
        
        if isinstance(obj, User) and obj.id == request.user.id:
            return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试操作对象 {obj}，权限不足'
        )
        return False
