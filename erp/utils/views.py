import logging
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from system.models import Log
from .permissions import HasModulePermission

logger = logging.getLogger(__name__)


class BaseModelViewSet(viewsets.ModelViewSet):
    """基础视图集，统一响应格式和操作日志记录"""

    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = None
    read_serializer_class = None
    log_display_field = 'name'
    log_exclude_fields = ['created_at', 'updated_at', 'id']

    def get_client_ip(self, request):
        """获取客户端 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_action(self, request, action, detail):
        """记录操作日志"""
        if not request.user.is_authenticated:
            return

        module = self.module_name or self.__class__.__name__.replace('ViewSet', '')
        try:
            Log.objects.create(
                user=request.user,
                action=action,
                module=module,
                detail=detail,
                ip_address=self.get_client_ip(request)
            )
        except Exception as e:
            logger.error(f'记录日志失败: {str(e)}')

    def get_display_name(self, instance):
        """获取实例的显示名称"""
        if hasattr(instance, self.log_display_field):
            return getattr(instance, self.log_display_field)
        if hasattr(instance, 'name'):
            return instance.name
        if hasattr(instance, 'username'):
            return instance.username
        if hasattr(instance, 'code'):
            return instance.code
        return f'ID={instance.id}'

    def get_changes(self, old_data, new_data):
        """获取变更详情"""
        changes = []
        for field, new_value in new_data.items():
            if field in self.log_exclude_fields:
                continue
            if field not in old_data:
                continue
            old_value = old_data[field]
            if old_value != new_value:
                field_display = self.get_field_display_name(field)
                old_display = self.format_value(old_value)
                new_display = self.format_value(new_value)
                changes.append(f'{field_display}: "{old_display}" → "{new_display}"')
        return changes

    def get_field_display_name(self, field):
        """获取字段的中文名称"""
        field_names = {
            'name': '姓名',
            'username': '用户名',
            'code': '编码',
            'status': '状态',
            'is_active': '状态',
            'phone': '手机号',
            'role': '角色',
            'category': '分类',
            'unit': '单位',
            'purchase_price': '进货价',
            'sale_price': '销售价',
            'retail_price': '零售价',
            'min_stock': '最低库存',
            'max_stock': '最高库存',
            'spec': '规格',
            'barcode': '条形码',
            'remark': '备注',
            'address': '地址',
            'contact': '联系人',
            'description': '描述',
            'sort_order': '排序',
            'parent': '上级分类',
        }
        return field_names.get(field, field)

    def format_value(self, value):
        """格式化值用于显示"""
        if value is None or value == '':
            return '空'
        if isinstance(value, bool):
            return '启用' if value else '禁用'
        if isinstance(value, int):
            if value == 1 and hasattr(self, 'log_display_field'):
                return '启用'
            if value == 0 and hasattr(self, 'log_display_field'):
                return '禁用'
        return str(value)

    def get_read_serializer_class(self):
        """获取读取序列化器类"""
        if self.read_serializer_class is not None:
            return self.read_serializer_class
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            try:
                page = self.paginate_queryset(queryset)
            except Exception as page_error:
                logger.warning(f'分页错误: {str(page_error)}')
                return Response({
                    'code': 200,
                    'msg': '成功',
                    'data': {
                        'items': [],
                        'count': queryset.count(),
                        'next': None,
                        'previous': None
                    }
                })
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'code': 200,
                'msg': '成功',
                'data': {
                    'items': serializer.data,
                    'total': len(serializer.data)
                }
            })
        except Exception as e:
            logger.error(f'列表查询失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': None
            }, status=500)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'code': 200,
                'msg': '成功',
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f'详情查询失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': None
            }, status=500)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            instance = serializer.instance
            display_name = self.get_display_name(instance)
            module = self.module_name or self.__class__.__name__.replace('ViewSet', '')
            detail = f'创建{module}: {display_name}'
            self.log_action(request, 'create', detail)
            
            return Response({
                'code': 200,
                'msg': '创建成功',
                'data': {'id': instance.id}
            })
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            from django.db.utils import IntegrityError
            if isinstance(e, ValidationError):
                error_messages = []
                for field, messages in e.detail.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            if hasattr(msg, 'string'):
                                error_messages.append(msg.string)
                            else:
                                error_messages.append(str(msg))
                    else:
                        error_messages.append(str(messages))
                return Response({
                    'code': 400,
                    'msg': error_messages[0] if error_messages else '数据验证失败',
                    'data': None
                }, status=400)
            if isinstance(e, IntegrityError):
                error_msg = str(e)
                if 'unique' in error_msg.lower() or '重复' in error_msg:
                    return Response({
                        'code': 400,
                        'msg': '该名称已存在，请使用其他名称',
                        'data': None
                    }, status=400)
                return Response({
                    'code': 400,
                    'msg': '数据完整性错误，请检查输入内容',
                    'data': None
                }, status=400)
            logger.error(f'创建失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'创建失败: {str(e)}',
                'data': None
            }, status=500)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            old_serializer = self.get_read_serializer_class()(instance)
            old_data = old_serializer.data.copy()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            instance.refresh_from_db()
            display_name = self.get_display_name(instance)
            module = self.module_name or self.__class__.__name__.replace('ViewSet', '')
            
            new_serializer = self.get_read_serializer_class()(instance)
            new_data = new_serializer.data
            
            changes = self.get_changes(old_data, new_data)
            if changes:
                detail = f'更新{module}「{display_name}」: {"; ".join(changes)}'
            else:
                detail = f'更新{module}「{display_name}」: 无变更'
            
            self.log_action(request, 'update', detail)
            
            return Response({
                'code': 200,
                'msg': '更新成功',
                'data': new_serializer.data
            })
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            if isinstance(e, ValidationError):
                error_messages = []
                for field, messages in e.detail.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            if hasattr(msg, 'string'):
                                error_messages.append(msg.string)
                            else:
                                error_messages.append(str(msg))
                    else:
                        error_messages.append(str(messages))
                return Response({
                    'code': 400,
                    'msg': error_messages[0] if error_messages else '数据验证失败',
                    'data': None
                }, status=400)
            logger.error(f'更新失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'更新失败: {str(e)}',
                'data': None
            }, status=500)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            display_name = self.get_display_name(instance)
            module = self.module_name or self.__class__.__name__.replace('ViewSet', '')
            detail = f'删除{module}: {display_name}'
            
            self.perform_destroy(instance)
            self.log_action(request, 'delete', detail)
            return Response({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        except Exception as e:
            logger.error(f'删除失败: {str(e)}')
            return Response({
                'code': 500,
                'msg': f'删除失败: {str(e)}',
                'data': None
            }, status=500)

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'items': data,
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            }
        })
