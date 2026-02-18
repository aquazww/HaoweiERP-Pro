from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, RoleSerializer, LogSerializer
from .models import Role, Log
from utils.views import BaseModelViewSet


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，统一响应格式"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'access': response.data['access'],
                'refresh': response.data['refresh']
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
    permission_classes = [IsAuthenticated]
    module_name = '角色'


class UserViewSet(BaseModelViewSet):
    """用户管理"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    module_name = '用户'
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()


class LogViewSet(BaseModelViewSet):
    """操作日志（只读）"""
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options']
    module_name = '操作日志'
