import logging
import csv
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model, authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer, 
    UserUpdateSerializer, LogSerializer, ResetPasswordSerializer, ClearLogsSerializer, PERMISSION_MODULES
)
from .models import Log
from .permissions import IsAdminUser, IsAdminOrReadOnly, ModulePermission
from utils.views import BaseModelViewSet

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，统一响应格式"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        if not username:
            return Response({
                'code': 401,
                'msg': '用户名或密码错误',
                'data': None
            }, status=401)

        user = None
        is_disabled = False

        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                is_disabled = True
        except User.DoesNotExist:
            pass

        django_response = None
        auth_failed = False
        if user and not is_disabled:
            try:
                django_response = super().post(request, *args, **kwargs)
            except Exception:
                auth_failed = True

        if not user or is_disabled or auth_failed or (user and not is_disabled and django_response is None):
            auth_failed = True

        if user and is_disabled:
            Log.objects.create(
                user=user,
                action='login',
                module='系统',
                detail=f'禁用账户尝试登录',
                ip_address=self.get_client_ip(request)
            )
            return Response({
                'code': 401,
                'msg': '您的账户已被禁用，请联系管理员',
                'data': {'reason': 'account_disabled'}
            }, status=401)

        if auth_failed:
            return Response({
                'code': 401,
                'msg': '用户名或密码错误',
                'data': None
            }, status=401)

        Log.objects.create(
            user=user,
            action='login',
            module='系统',
            detail=f'用户登录成功',
            ip_address=self.get_client_ip(request)
        )

        from django.conf import settings
        from django.http import JsonResponse

        response_data = JsonResponse({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'permissions': user.get_all_permissions(),
                'username': user.username,
                'expires_in': 7200
            }
        })

        response_data.set_cookie(
            'access_token',
            django_response.data['access'],
            max_age=7200,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/'
        )

        response_data.set_cookie(
            'refresh_token',
            django_response.data['refresh'],
            max_age=604800,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/api/v1/auth/refresh/'
        )

        return response_data
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenRefreshView(TokenRefreshView):
    """自定义Token刷新视图，统一响应格式"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({
                'code': 401,
                'msg': '未找到刷新令牌',
                'data': None
            }, status=401)
        
        # 避免直接修改不可变的 request.data
        request._full_data = {'refresh': refresh_token}
        response = super().post(request, *args, **kwargs)
        
        from django.conf import settings
        from django.http import JsonResponse
        
        response_data = JsonResponse({
            'code': 200,
            'msg': '刷新成功',
            'data': {}
        })
        
        response_data.set_cookie(
            'access_token',
            response.data['access'],
            max_age=7200,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/'
        )
        
        if response.data.get('refresh'):
            response_data.set_cookie(
                'refresh_token',
                response.data['refresh'],
                max_age=604800,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                path='/api/v1/auth/refresh/'
            )
        
        return response_data


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'msg': '成功',
            'data': serializer.data
        })


class LogoutView(APIView):
    """登出视图，清除Cookie"""
    permission_classes = [AllowAny]

    def post(self, request):
        from django.http import JsonResponse

        # 记录登出日志
        if request.user.is_authenticated:
            Log.objects.create(
                user=request.user,
                action='logout',
                module='系统',
                detail=f'用户登出',
                ip_address=self.get_client_ip(request)
            )

        response = JsonResponse({
            'code': 200,
            'msg': '登出成功',
            'data': None
        })
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class UserViewSet(BaseModelViewSet):
    """用户管理"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    read_serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ModulePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['username', 'phone']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']
    module_name = '用户'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_display_name(self, instance):
        """获取用户显示名称，合并用户名和姓名"""
        if instance.name:
            return f'{instance.username}（{instance.name}）'
        return instance.username

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f'用户 {self.request.user.username} 创建了新用户 {user.username}')

    def perform_update(self, serializer):
        instance = serializer.instance
        old_permissions = instance.permissions if instance.permissions else {}
        old_is_active = instance.is_active
        user = serializer.save()
        new_permissions = user.permissions if user.permissions else {}
        new_is_active = user.is_active
        
        if old_permissions != new_permissions:
            user.invalidate_tokens()
            logger.info(f'用户 {user.username} 权限已变更，已使token失效')
        
        if old_is_active != new_is_active:
            user.invalidate_tokens()
            logger.info(f'用户 {user.username} 状态已变更，已使token失效')
        
        logger.info(f'用户 {self.request.user.username} 更新了用户 {user.username}')

    def perform_destroy(self, instance):
        if instance.username == 'admin':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('不能删除管理员账户')
        username = instance.username
        instance.delete()
        logger.info(f'用户 {self.request.user.username} 删除了用户 {username}')

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.invalidate_tokens()
        user.save()  # 保存密码更改到数据库
        
        self.log_action(request, 'update', f'重置用户密码: {user.username}')
        logger.info(f'用户 {request.user.username} 重置了用户 {user.username} 的密码')
        
        return Response({
            'code': 200,
            'msg': '密码重置成功，用户需重新登录',
            'data': None
        })

    @action(detail=False, methods=['get'])
    def permission_modules(self, request):
        """获取权限模块列表"""
        return Response({
            'code': 200,
            'msg': '成功',
            'data': PERMISSION_MODULES
        })


class LogViewSet(BaseModelViewSet):
    """操作日志（只读）"""
    queryset = Log.objects.select_related('user').all()
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated, ModulePermission]
    http_method_names = ['get', 'head', 'options', 'post']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'action', 'module']
    search_fields = ['detail']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    module_name = '操作日志'

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出操作日志为 CSV 文件"""
        queryset = self.filter_queryset(self.get_queryset())
        response = StreamingHttpResponse(
            streaming_content=self._generate_csv(queryset),
            content_type='text/csv; charset=utf-8-sig'
        )
        response['Content-Disposition'] = 'attachment; filename="operation_logs.csv"'
        return response

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """清空操作日志 —— 需要管理员密码验证"""
        serializer = ClearLogsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']

        user = authenticate(request, username=request.user.username, password=password)
        if user is None:
            return Response(
                {'code': 400, 'msg': '管理员密码验证失败，请检查密码是否正确'},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser and not request.user.is_staff:
            return Response(
                {'code': 403, 'msg': '仅管理员可执行此操作'},
                status=http_status.HTTP_403_FORBIDDEN
            )

        deleted_count, _ = Log.objects.all().delete()
        logger.warning(
            f'用户 {request.user.username}(IP:{self.get_client_ip(request)}) 清空了操作日志，共 {deleted_count} 条'
        )
        return Response({
            'code': 200,
            'msg': f'操作日志已清空，共删除 {deleted_count} 条记录',
            'data': {'deleted_count': deleted_count}
        })

    def _generate_csv(self, queryset):
        """生成 CSV 数据流的生成器"""
        yield '\ufeff'
        writer = csv.writer(self._echo())
        writer.writerow(['操作用户', '操作类型', '操作模块', '操作详情', 'IP地址', '操作时间'])

        action_map = {
            'create': '创建', 'update': '更新', 'delete': '删除',
            'login': '登录', 'logout': '登出', 'cancel': '取消',
            'confirm': '确认', 'confirm_inbound': '确认入库',
            'update_status': '状态变更', 'other': '其他'
        }

        for log in queryset.iterator(chunk_size=500):
            row = [
                log.user.name or log.user.username if log.user else '-',
                action_map.get(log.action, log.action),
                log.module or '-',
                log.detail or '-',
                log.ip_address or '-',
                log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '-'
            ]
            yield writer.writerow(row)

    class Echo:
        def write(self, value):
            return value

    def _echo(self):
        return self.Echo()
