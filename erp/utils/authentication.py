from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """
    从HttpOnly Cookie读取JWT Token的认证类
    """
    
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            return None
        
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError):
            return None
    
    def get_validated_token(self, raw_token):
        return super().get_validated_token(raw_token.encode() if isinstance(raw_token, str) else raw_token)
