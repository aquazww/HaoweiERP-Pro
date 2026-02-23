import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer, 
    UserUpdateSerializer, LogSerializer, ResetPasswordSerializer, PERMISSION_MODULES
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
        
        try:
            user = User.objects.get(username=username)
            
            if not user.is_active:
                Log.objects.create(
                    user=user,
                    action='login',
                    module='系统',
                    detail=f'禁用账户 {user.username} 尝试登录',
                    ip_address=self.get_client_ip(request)
                )
                return Response({
                    'code': 401,
                    'msg': '账户已被禁用，请联系管理员',
                    'data': None
                }, status=401)
            
            response = super().post(request, *args, **kwargs)
            
            Log.objects.create(
                user=user,
                action='login',
                module='系统',
                detail=f'用户 {user.username} 登录成功',
                ip_address=self.get_client_ip(request)
            )
            
            from django.conf import settings
            from django.http import JsonResponse
            
            response_data = JsonResponse({
                'code': 200,
                'msg': '登录成功',
                'data': {
                    'permissions': user.get_all_permissions(),
                    'username': user.username
                }
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
            
        except User.DoesNotExist:
            return Response({
                'code': 401,
                'msg': '用户名或密码错误',
                'data': None
            }, status=401)
        except Exception as e:
            error_msg = str(e)
            if 'detail' in error_msg or '用户名或密码' in error_msg:
                return Response({
                    'code': 401,
                    'msg': '用户名或密码错误',
                    'data': None
                }, status=401)
            return Response({
                'code': 401,
                'msg': '登录失败，请检查用户名和密码',
                'data': None
            }, status=401)
    
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
        
        request.data['refresh'] = refresh_token
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
        response = JsonResponse({
            'code': 200,
            'msg': '登出成功',
            'data': None
        })
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


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

    def perform_create(self, serializer):
        user = serializer.save()
        self.log_action(self.request, 'create', f'创建用户: {user.username}')
        logger.info(f'用户 {self.request.user.username} 创建了新用户 {user.username}')

    def perform_update(self, serializer):
        instance = serializer.instance
        old_permissions = instance.permissions if instance.permissions else {}
        user = serializer.save()
        new_permissions = user.permissions if user.permissions else {}
        
        if old_permissions != new_permissions:
            user.invalidate_tokens()
            logger.info(f'用户 {user.username} 权限已变更，已使token失效')
        
        self.log_action(self.request, 'update', f'更新用户: {user.username}')
        logger.info(f'用户 {self.request.user.username} 更新了用户 {user.username}')

    def perform_destroy(self, instance):
        if instance.username == 'admin':
            raise ValueError('不能删除管理员账户')
        username = instance.username
        instance.delete()
        self.log_action(self.request, 'delete', f'删除用户: {username}')
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
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'action', 'module']
    search_fields = ['detail']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    module_name = '操作日志'
