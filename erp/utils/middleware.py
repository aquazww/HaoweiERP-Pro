import logging
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class TokenVersionMiddleware:
    """
    验证Token版本的中间件
    当用户的token_version发生变化时，使旧token失效
    """
    
    EXEMPT_PATHS = [
        '/api/v1/auth/login/',
        '/api/v1/auth/refresh/',
        '/api/v1/auth/register/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.path.startswith('/api/'):
            return None
        
        for exempt_path in self.EXEMPT_PATHS:
            if request.path == exempt_path:
                return None
        
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None
        
        auth = JWTAuthentication()
        try:
            raw_token = access_token.encode() if isinstance(access_token, str) else access_token
            validated_token = auth.get_validated_token(raw_token)
            user_id = validated_token.get('user_id')
            token_version = validated_token.get('token_version', 0)
            
            try:
                user = User.objects.get(id=user_id)
                if user.token_version != token_version:
                    logger.info(f'用户 {user.username} 的token已失效，token_version不匹配')
                    response = JsonResponse({
                        'code': 401,
                        'msg': '您的账户权限已变更，请重新登录',
                        'data': None
                    }, status=401)
                    response.delete_cookie('access_token')
                    response.delete_cookie('refresh_token')
                    return response
            except User.DoesNotExist:
                pass
            
        except (InvalidToken, TokenError) as e:
            logger.debug(f'Token验证失败: {str(e)}')
        except Exception as e:
            logger.error(f'TokenVersionMiddleware error: {str(e)}')
        
        return None
