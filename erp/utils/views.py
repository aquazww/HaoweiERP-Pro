from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from system.models import Log
from .permissions import HasModulePermission


class BaseModelViewSet(viewsets.ModelViewSet):
    """基础视图集，统一响应格式和操作日志记录"""

    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = None

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
        except Exception:
            pass

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'msg': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.log_action(request, 'create', f'创建数据: {serializer.data}')
        return Response({
            'code': 200,
            'msg': '创建成功',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_data = str(instance.__dict__)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.log_action(request, 'update', f'更新数据: 旧值={old_data[:500]}..., 新值={str(serializer.data)}')
        return Response({
            'code': 200,
            'msg': '更新成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = str(instance.__dict__)
        self.perform_destroy(instance)
        self.log_action(request, 'delete', f'删除数据: {old_data[:500]}...')
        return Response({
            'code': 200,
            'msg': '删除成功',
            'data': None
        })

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'items': data,
                'count': self.paginator.page.paginator.count,
                'next': None,
                'previous': None
            }
        })
