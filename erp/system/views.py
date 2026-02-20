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
    UserUpdateSerializer, RoleSerializer, LogSerializer, ResetPasswordSerializer
)
from .models import Role, Log
from .permissions import IsAdminUser, IsAdminOrReadOnly
from utils.views import BaseModelViewSet

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，统一响应格式"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data.get('username'))
        
        Log.objects.create(
            user=user,
            action='login',
            module='系统',
            detail=f'用户 {user.username} 登录成功',
            ip_address=self.get_client_ip(request)
        )
        
        return Response({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'access': response.data['access'],
                'refresh': response.data['refresh']
            }
        })
    
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
        response = super().post(request, *args, **kwargs)
        return Response({
            'code': 200,
            'msg': '刷新成功',
            'data': {
                'access': response.data['access'],
                'refresh': response.data.get('refresh')
            }
        })


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


class RoleViewSet(BaseModelViewSet):
    """角色管理"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    module_name = '角色'


class UserViewSet(BaseModelViewSet):
    """用户管理"""
    queryset = User.objects.select_related('role').all()
    serializer_class = UserSerializer
    read_serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'role']
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
        user = serializer.save()
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
        user.save()
        
        self.log_action(request, 'update', f'重置用户密码: {user.username}')
        logger.info(f'用户 {request.user.username} 重置了用户 {user.username} 的密码')
        
        return Response({
            'code': 200,
            'msg': '密码重置成功',
            'data': None
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
