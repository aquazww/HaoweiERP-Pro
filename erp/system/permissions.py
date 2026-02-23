import logging
from rest_framework import permissions
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员或有系统管理权限的用户访问
    """
    message = '您没有权限执行此操作，请联系管理员'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            logger.warning(f'未认证用户尝试访问: {request.path}')
            return False
        
        if request.user.username == 'admin':
            return True
        
        if hasattr(request.user, 'has_permission'):
            if request.user.has_permission('system', 'view'):
                return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试访问 {request.path}，权限不足'
        )
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员或有权限的用户可以执行所有操作，其他用户只能读取
    """
    message = '您没有权限执行此操作，请联系管理员'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.username == 'admin':
            return True
        
        if hasattr(request.user, 'has_permission'):
            action = self._get_action_from_method(request.method)
            if request.user.has_permission('system', action):
                return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试执行 {request.method} 操作，权限不足'
        )
        return False
    
    def _get_action_from_method(self, method):
        action_map = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'edit',
            'PATCH': 'edit',
            'DELETE': 'delete'
        }
        return action_map.get(method, 'view')


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
        
        if hasattr(request.user, 'has_permission'):
            if request.user.has_permission('system', 'edit'):
                return True
        
        if isinstance(obj, User) and obj.id == request.user.id:
            return True
        
        logger.warning(
            f'用户 {request.user.username} 尝试操作对象 {obj}，权限不足'
        )
        return False


class ModulePermission(permissions.BasePermission):
    """
    通用模块权限检查类
    根据视图的 module_name 属性自动检查对应模块的权限
    """
    
    METHOD_ACTION_MAP = {
        'GET': 'view',
        'POST': 'add',
        'PUT': 'edit',
        'PATCH': 'edit',
        'DELETE': 'delete'
    }
    
    MODULE_MAP = {
        '计量单位': 'basic',
        '商品分类': 'basic',
        '仓库': 'basic',
        '供应商': 'basic',
        '客户': 'basic',
        '商品': 'basic',
        '采购订单': 'purchase',
        '销售订单': 'sale',
        '库存查询': 'inventory',
        '库存入库': 'inventory',
        '库存出库': 'inventory',
        '库存调整': 'inventory',
        '库存调拨': 'inventory',
        '库存流水': 'inventory',
        '收付款': 'finance',
        '用户': 'system',
        '操作日志': 'system',
        '采购报表': 'reports',
        '销售报表': 'reports',
        '库存报表': 'reports',
        '财务报表': 'reports',
    }
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.username == 'admin':
            return True
        
        module_name = getattr(view, 'module_name', None)
        if not module_name:
            return True
        
        module = self.MODULE_MAP.get(module_name)
        if not module:
            return True
        
        action = self.METHOD_ACTION_MAP.get(request.method, 'view')
        
        if hasattr(request.user, 'has_permission'):
            has_perm = request.user.has_permission(module, action)
            if not has_perm:
                action_names = {'view': '查看', 'add': '新增', 'edit': '编辑', 'delete': '删除'}
                self.message = f'您没有{module_name}的{action_names.get(action, action)}权限'
                logger.warning(
                    f'用户 {request.user.username} 尝试 {action} {module_name}，权限不足'
                )
            return has_perm
        
        return False


class ModulePermissionMixin:
    """
    模块权限混入类
    在ViewSet中使用：permission_classes = [IsAuthenticated, ModulePermission]
    """
    permission_classes = [permissions.IsAuthenticated, ModulePermission]
