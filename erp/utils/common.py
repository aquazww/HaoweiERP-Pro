from rest_framework.response import Response


def success_response(data=None, msg='操作成功', code=200):
    """统一成功响应"""
    return Response({
        'code': code,
        'msg': msg,
        'data': data
    })


def error_response(msg='操作失败', code=400):
    """统一错误响应"""
    return Response({
        'code': code,
        'msg': msg,
        'data': None
    })
