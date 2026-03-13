import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated, ValidationError
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
        elif isinstance(exc, ValidationError):
            errors = exc.detail
            messages = []
            error_fields = []
            field_names = {
                # 公司信息
                'website': '公司网站',
                'email': '电子邮箱',
                'phone': '联系电话',
                'fax': '传真号码',
                'credit_code': '统一社会信用代码',
                'tax_number': '纳税人识别号',
                'bank_account': '银行账号',
                'name': '名称',
                'short_name': '公司简称',
                'legal_person': '法定代表人',
                'registered_address': '注册地址',
                'business_address': '经营地址',
                'bank_name': '开户银行',
                'invoice_title': '发票抬头',
                'remark': '备注',
                'logo': '公司Logo',
                'stamp': '公司印章',
                # 计量单位
                'unit': '单位',
                'unit_name': '单位名称',
                # 商品
                'code': '编码',
                'goods': '商品',
                'goods_name': '商品名称',
                'goods_code': '商品编码',
                'goods_spec': '规格型号',
                'category': '分类',
                'purchase_price': '采购价',
                'sale_price': '销售价',
                'min_stock': '最低库存',
                'max_stock': '最高库存',
                'status': '状态',
                'is_active': '是否启用',
                # 仓库
                'warehouse': '仓库',
                'warehouse_name': '仓库名称',
                'address': '地址',
                'contact': '联系人',
                # 供应商/客户
                'supplier': '供应商',
                'supplier_name': '供应商名称',
                'customer': '客户',
                'customer_name': '客户名称',
                'customer_contact': '客户联系人',
                'customer_phone': '客户电话',
                'customer_address': '客户地址',
                # 采购/销售订单
                'order_no': '订单编号',
                'order_date': '订单日期',
                'total_amount': '总金额',
                'quantity': '数量',
                'price': '单价',
                'amount': '金额',
                # 库存
                'stock': '库存',
                'stock_quantity': '库存数量',
                'change_type': '变动类型',
                'change_quantity': '变动数量',
                'before_quantity': '变动前数量',
                'after_quantity': '变动后数量',
                # 财务
                'payment_type': '付款类型',
                'payment_method': '付款方式',
                'payment_amount': '付款金额',
                'payment_date': '付款日期',
                # 用户
                'username': '用户名',
                'password': '密码',
                'password2': '确认密码',
                'real_name': '真实姓名',
                'role': '角色',
                'new_password': '新密码',
                'confirm_password': '确认密码',
            }
            if isinstance(errors, dict):
                for field, msgs in errors.items():
                    field_name = field_names.get(field, field)
                    error_fields.append(field)
                    if isinstance(msgs, list):
                        for msg in msgs:
                            messages.append(f'{field_name}{msg}')
                    else:
                        messages.append(f'{field_name}{msgs}')
            elif isinstance(errors, list):
                for msg in errors:
                    messages.append(str(msg))
            else:
                messages.append(str(errors))
            
            response.data = {
                'code': 400,
                'msg': '；'.join(messages),
                'data': {'fields': error_fields} if error_fields else None
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
