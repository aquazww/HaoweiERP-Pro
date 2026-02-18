from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Role, Log


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义 JWT 序列化器"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        if user.role:
            token['role'] = user.role.name
        return token


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_name', 'phone', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LogSerializer(serializers.ModelSerializer):
    """日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Log
        fields = ['id', 'user', 'username', 'action', 'module', 'detail', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']
