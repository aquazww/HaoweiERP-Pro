"""
订单号生成工具模块
"""
from django.utils import timezone
from django.db import models


def generate_order_no(prefix='PO', model_class=None, field_name='order_no'):
    """
    生成订单号
    格式: 前缀 + 年月日 + 4位序号 (例如: PO202602180001)
    
    :param prefix: 订单号前缀
    :param model_class: 模型类（用于查询当日最大序号）
    :param field_name: 订单号字段名
    :return: 生成的订单号
    """
    today = timezone.now().strftime('%Y%m%d')
    prefix_with_date = f'{prefix}{today}'
    
    if model_class:
        queryset = model_class.objects.filter(
            **{f'{field_name}__startswith': prefix_with_date}
        ).order_by(f'-{field_name}')
        
        last_order = queryset.first()
        
        if last_order:
            last_no = getattr(last_order, field_name)
            try:
                last_seq = int(last_no[-4:])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1
    else:
        new_seq = 1
    
    return f'{prefix_with_date}{new_seq:04d}'


def generate_purchase_order_no():
    """生成采购订单号"""
    from purchase.models import PurchaseOrder
    return generate_order_no(prefix='PO', model_class=PurchaseOrder)


def generate_stock_in_no():
    """生成入库单号"""
    from inventory.models import StockIn
    return generate_order_no(prefix='SI', model_class=StockIn)


def generate_stock_out_no():
    """生成出库单号"""
    from inventory.models import StockOut
    return generate_order_no(prefix='SO', model_class=StockOut)


def generate_sale_order_no():
    """生成销售订单号"""
    from sale.models import SaleOrder
    return generate_order_no(prefix='SO', model_class=SaleOrder)


def generate_stock_adjust_no():
    """生成库存调整单号"""
    from inventory.models import StockAdjust
    return generate_order_no(prefix='SA', model_class=StockAdjust)


def generate_stock_transfer_no():
    """生成库存调拨单号"""
    from inventory.models import StockTransfer
    return generate_order_no(prefix='ST', model_class=StockTransfer)
