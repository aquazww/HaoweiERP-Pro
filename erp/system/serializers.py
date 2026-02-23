from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Log

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义 JWT 序列化器"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['token_version'] = user.token_version
        token['permissions'] = user.get_all_permissions()
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(username=username)
            
            if not user.is_active:
                raise serializers.ValidationError('账户已被禁用，请联系管理员')
            
            if not user.check_password(password):
                raise serializers.ValidationError('用户名或密码错误')
                
        except User.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')
        
        return super().validate(attrs)


PERMISSION_MODULES = {
    'basic': {'name': '基础资料', 'actions': ['view', 'add', 'edit', 'delete']},
    'purchase': {'name': '采购管理', 'actions': ['view', 'add', 'edit', 'delete']},
    'sale': {'name': '销售管理', 'actions': ['view', 'add', 'edit', 'delete']},
    'inventory': {'name': '库存管理', 'actions': ['view', 'add', 'edit', 'delete']},
    'finance': {'name': '财务管理', 'actions': ['view', 'add', 'edit', 'delete']},
    'reports': {'name': '报表中心', 'actions': ['view']},
    'system': {'name': '系统管理', 'actions': ['view', 'add', 'edit', 'delete']}
}


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    permissions_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'permissions', 'permissions_display', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_permissions_display(self, obj):
        """获取权限显示信息"""
        return PERMISSION_MODULES
    
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
    
    def validate_name(self, value):
        """验证姓名"""
        if value and len(value) > 50:
            raise serializers.ValidationError('姓名不能超过50个字符')
        return value.strip() if value else ''
    
    def validate_phone(self, value):
        """验证手机号"""
        if value:
            import re
            if not re.match(r'^1[3-9]\d{9}$', value):
                raise serializers.ValidationError('请输入有效的手机号码')
        return value
    
    def validate_permissions(self, value):
        """验证权限格式并处理权限依赖"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('权限必须是字典格式')
        
        for module, perms in value.items():
            if module not in PERMISSION_MODULES:
                raise serializers.ValidationError(f'无效的权限模块: {module}')
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f'权限操作必须是字典格式: {module}')
            
            if perms.get('add') or perms.get('edit') or perms.get('delete'):
                perms['view'] = True
        
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6, required=True, help_text='密码，至少6位字符')
    password_confirm = serializers.CharField(write_only=True, required=True, help_text='确认密码，需与密码一致')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'password', 'password_confirm', 'phone', 'permissions', 'is_active']
        read_only_fields = ['id']
    
    def validate_name(self, value):
        """验证姓名"""
        if value and len(value) > 50:
            raise serializers.ValidationError('姓名不能超过50个字符')
        return value.strip() if value else ''
    
    def validate_password(self, value):
        """验证密码格式"""
        if len(value) < 6:
            raise serializers.ValidationError('密码长度不能少于6位字符')
        return value
    
    def validate_permissions(self, value):
        """验证权限格式并处理权限依赖"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('权限必须是字典格式')
        
        for module, perms in value.items():
            if module not in PERMISSION_MODULES:
                raise serializers.ValidationError(f'无效的权限模块: {module}')
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f'权限操作必须是字典格式: {module}')
            
            if perms.get('add') or perms.get('edit') or perms.get('delete'):
                perms['view'] = True
        
        return value
    
    def validate(self, data):
        """验证两次密码是否一致"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码输入不一致，请确保两次输入的密码相同'})
        return data
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'permissions']
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {'required': False},
            'name': {'required': False},
            'phone': {'required': False},
            'permissions': {'required': False}
        }
    
    def validate_name(self, value):
        """验证姓名"""
        if value and len(value) > 50:
            raise serializers.ValidationError('姓名不能超过50个字符')
        return value.strip() if value else ''
    
    def validate_permissions(self, value):
        """验证权限格式并处理权限依赖"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('权限必须是字典格式')
        
        for module, perms in value.items():
            if module not in PERMISSION_MODULES:
                raise serializers.ValidationError(f'无效的权限模块: {module}')
            if not isinstance(perms, dict):
                raise serializers.ValidationError(f'权限操作必须是字典格式: {module}')
            
            if perms.get('add') or perms.get('edit') or perms.get('delete'):
                perms['view'] = True
        
        return value
    
    def update(self, instance, validated_data):
        """更新用户"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LogSerializer(serializers.ModelSerializer):
    """日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Log
        fields = ['id', 'user', 'username', 'user_name', 'action', 'module', 'detail', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    new_password = serializers.CharField(min_length=6, max_length=50)
    
    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('密码长度不能少于6位')
        return value
