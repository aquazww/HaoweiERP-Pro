import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        if isinstance(exc, PermissionDenied):
            detail = str(exc.detail) if hasattr(exc, 'detail') else '权限不足'
            response.data = {
                'code': 403,
                'msg': f'权限不足：{detail}',
                'data': None
            }
            response.status_code = 200
            logger.warning(f'权限拒绝: {context.get("view", "")} - {detail}')
        elif isinstance(exc, NotAuthenticated):
            response.data = {
                'code': 401,
                'msg': '请先登录',
                'data': None
            }
            response.status_code = 200
        elif isinstance(exc, AuthenticationFailed):
            response.data = {
                'code': 401,
                'msg': '认证失败',
                'data': None
            }
            response.status_code = 200
        else:
            if isinstance(response.data, dict):
                if 'code' not in response.data:
                    response.data = {
                        'code': response.status_code,
                        'msg': response.data.get('detail', '请求失败'),
                        'data': response.data
                    }
            elif isinstance(response.data, list):
                response.data = {
                    'code': response.status_code,
                    'msg': '请求失败',
                    'data': response.data
                }
            response.status_code = 200
    
    return response
