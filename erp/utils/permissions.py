"""
权限控制模块
"""
from rest_framework import permissions
from rest_framework.response import Response


class HasModulePermission(permissions.BasePermission):
    """
    基于模块的权限控制
    使用方法：permission_classes = [IsAuthenticated, HasModulePermission]
    需要在视图中设置 module_name 属性
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级用户拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 获取用户角色
        role = request.user.role
        if not role:
            return False
        
        # 获取模块名称
        module_name = getattr(view, 'module_name', None)
        if not module_name:
            return True
        
        # 将中文模块名映射到权限键
        module_mapping = {
            '商品分类': 'basic',
            '仓库': 'basic',
            '供应商': 'basic',
            '客户': 'basic',
            '商品': 'basic',
            '角色': 'system',
            '用户': 'system',
            '操作日志': 'system',
            '库存': 'inventory',
            '库存流水': 'inventory',
            '入库单': 'inventory',
            '出库单': 'inventory',
            '采购单': 'purchase',
            '采购明细': 'purchase',
            '销售单': 'sale',
            '销售明细': 'sale',
            '收付款': 'finance',
        }
        
        permission_key = module_mapping.get(module_name, module_name.lower())
        
        # 检查权限
        permissions_dict = role.permissions or {}
        return permissions_dict.get(permission_key, False)


class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员访问
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or 
            (request.user.role and request.user.role.name == '管理员')
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    仅允许所有者或管理员访问
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if request.user.role and request.user.role.name == '管理员':
            return True
        
        # 检查对象是否有 created_by 字段
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # 检查对象是否有 user 字段
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


def check_permission(module_name):
    """
    权限检查装饰器
    用于视图方法
    """
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            
            if not user or not user.is_authenticated:
                return Response({
                    'code': 401,
                    'msg': '请先登录',
                    'data': None
                })
            
            if user.is_superuser:
                return func(self, request, *args, **kwargs)
            
            role = user.role
            if not role:
                return Response({
                    'code': 403,
                    'msg': '您没有访问权限',
                    'data': None
                })
            
            # 模块名映射
            module_mapping = {
                'basic': 'basic',
                'purchase': 'purchase',
                'sale': 'sale',
                'inventory': 'inventory',
                'finance': 'finance',
                'reports': 'reports',
                'system': 'system',
            }
            
            permission_key = module_mapping.get(module_name, module_name)
            permissions_dict = role.permissions or {}
            
            if not permissions_dict.get(permission_key, False):
                return Response({
                    'code': 403,
                    'msg': '您没有访问该模块的权限',
                    'data': None
                })
            
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator
