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
            
            instance_id = serializer.instance.id if serializer.instance else ''
            self.log_action(request, 'create', f'创建数据: ID={instance_id}')
            
            return Response({
                'code': 200,
                'msg': '创建成功',
                'data': {'id': instance_id}
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
            instance_id = instance.id
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            self.log_action(request, 'update', f'更新数据: ID={instance_id}')
            
            instance.refresh_from_db()
            read_serializer_class = self.get_read_serializer_class()
            read_serializer = read_serializer_class(instance)
            
            return Response({
                'code': 200,
                'msg': '更新成功',
                'data': read_serializer.data
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
            instance_id = instance.id
            self.perform_destroy(instance)
            self.log_action(request, 'delete', f'删除数据: ID={instance_id}')
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
