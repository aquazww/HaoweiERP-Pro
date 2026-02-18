from django.db import models
from django.utils import timezone


def generate_order_no(prefix='PO'):
    """
    生成订单号
    格式: PO + 年月日 + 4位序号 (例如: PO202602180001)
    """
    today = timezone.now().strftime('%Y%m%d')
    from purchase.models import PurchaseOrder
    
    last_order = PurchaseOrder.objects.filter(
        order_no__startswith=f'{prefix}{today}'
    ).order_by('-order_no').first()
    
    if last_order:
        last_seq = int(last_order.order_no[-4:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f'{prefix}{today}{new_seq:04d}'
