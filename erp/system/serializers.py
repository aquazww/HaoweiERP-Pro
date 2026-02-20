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
    
    def validate_name(self, value):
        """验证角色名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('角色名称不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('角色名称不能超过50个字符')
        return value.strip()
    
    def validate_description(self, value):
        """验证描述"""
        if value and len(value) > 200:
            raise serializers.ValidationError('描述不能超过200个字符')
        return value
    
    def validate_permissions(self, value):
        """验证权限列表"""
        valid_permissions = ['basic', 'purchase', 'sale', 'inventory', 'finance', 'reports', 'system']
        if not isinstance(value, dict):
            raise serializers.ValidationError('权限必须是字典格式')
        
        for key in value.keys():
            if key not in valid_permissions:
                raise serializers.ValidationError(f'无效的权限模块: {key}')
        
        return value


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_name', 'phone', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_username(self, value):
        """验证用户名"""
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        if len(value) > 150:
            raise serializers.ValidationError('用户名不能超过150个字符')
        import re
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('用户名只能包含字母、数字和@/./+/-/_字符')
        return value.strip()
    
    def validate_phone(self, value):
        """验证手机号"""
        if value:
            import re
            if not re.match(r'^1[3-9]\d{9}$', value):
                raise serializers.ValidationError('请输入有效的手机号码')
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password_confirm', 'role', 'phone', 'is_active']
        read_only_fields = ['id']
    
    def validate(self, data):
        """验证两次密码是否一致"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码输入不一致'})
        return data
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LogSerializer(serializers.ModelSerializer):
    """日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Log
        fields = ['id', 'user', 'username', 'action', 'module', 'detail', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']
