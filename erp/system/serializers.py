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

    def validate(self, attrs):
        """
        验证用户登录，检查账户状态
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(username=username)
            
            # 检查账户是否被禁用
            if not user.is_active:
                raise serializers.ValidationError('账户已被禁用，请联系管理员')
            
            # 验证密码
            if not user.check_password(password):
                raise serializers.ValidationError('用户名或密码错误')
                
        except User.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')
        
        return super().validate(attrs)


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'validators': []
            }
        }
    
    def validate_name(self, value):
        """验证角色名称"""
        if not value or not value.strip():
            raise serializers.ValidationError('角色名称不能为空')
        if len(value) > 50:
            raise serializers.ValidationError('角色名称不能超过50个字符')
        
        value = value.strip()
        
        queryset = Role.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(f'角色名称「{value}」已存在，请使用其他名称')
        
        return value
    
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
        fields = ['id', 'username', 'name', 'role', 'role_name', 'phone', 'is_active', 'created_at']
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


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6, required=True, help_text='密码，至少6位字符')
    password_confirm = serializers.CharField(write_only=True, required=True, help_text='确认密码，需与密码一致')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'password', 'password_confirm', 'role', 'phone', 'is_active']
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
    password = serializers.CharField(write_only=True, min_length=6, required=False, allow_blank=True, help_text='密码（留空则不修改），至少6位字符')
    password_confirm = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text='确认密码，修改密码时需与密码一致')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'password', 'password_confirm', 'role', 'phone', 'is_active']
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {'required': False},
            'name': {'required': False},
            'role': {'required': False},
            'phone': {'required': False}
        }
    
    def validate_name(self, value):
        """验证姓名"""
        if value and len(value) > 50:
            raise serializers.ValidationError('姓名不能超过50个字符')
        return value.strip() if value else ''
    
    def validate_password(self, value):
        """验证密码格式"""
        if value and len(value) < 6:
            raise serializers.ValidationError('密码长度不能少于6位字符')
        return value
    
    def validate(self, data):
        """验证两次密码是否一致"""
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if password or password_confirm:
            if not password:
                raise serializers.ValidationError({'password': '请输入密码'})
            if not password_confirm:
                raise serializers.ValidationError({'password_confirm': '请再次输入密码以确认'})
            if password != password_confirm:
                raise serializers.ValidationError({'password_confirm': '两次密码输入不一致，请确保两次输入的密码相同'})
        
        return data
    
    def update(self, instance, validated_data):
        """更新用户"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
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
