from django.db import transaction
from .models import Inventory, InventoryLog


class InventoryService:
    """库存服务类"""

    @staticmethod
    @transaction.atomic
    def stock_in(goods, warehouse, quantity, related_order=None, remark='', created_by=None):
        """
        入库操作
        :param goods: 商品对象
        :param warehouse: 仓库对象
        :param quantity: 入库数量
        :param related_order: 关联单据对象
        :param remark: 备注
        :param created_by: 操作人
        """
        if quantity <= 0:
            raise ValueError('入库数量必须大于0')
        
        inventory, created = Inventory.objects.get_or_create(
            goods=goods,
            warehouse=warehouse,
            defaults={'quantity': 0}
        )
        
        old_quantity = inventory.quantity
        inventory.quantity += quantity
        inventory.save()
        
        log_data = {
            'goods': goods,
            'warehouse': warehouse,
            'change_type': 'inbound',
            'change_quantity': quantity,
            'before_quantity': old_quantity,
            'after_quantity': inventory.quantity,
            'remark': remark,
            'created_by': created_by
        }
        
        if related_order:
            log_data['related_order_type'] = related_order.__class__.__name__
            log_data['related_order_id'] = related_order.id
        
        InventoryLog.objects.create(**log_data)
        
        return inventory

    @staticmethod
    @transaction.atomic
    def stock_out(goods, warehouse, quantity, related_order=None, remark='', created_by=None):
        """
        出库操作
        :param goods: 商品对象
        :param warehouse: 仓库对象
        :param quantity: 出库数量
        :param related_order: 关联单据对象
        :param remark: 备注
        :param created_by: 操作人
        """
        if quantity <= 0:
            raise ValueError('出库数量必须大于0')
        
        try:
            inventory = Inventory.objects.get(
                goods=goods,
                warehouse=warehouse
            )
        except Inventory.DoesNotExist:
            raise ValueError(f'商品 {goods.name} 在该仓库无库存')
        
        if inventory.quantity < quantity:
            raise ValueError(f'商品 {goods.name} 库存不足，当前库存：{inventory.quantity}')
        
        old_quantity = inventory.quantity
        inventory.quantity -= quantity
        inventory.save()
        
        log_data = {
            'goods': goods,
            'warehouse': warehouse,
            'change_type': 'outbound',
            'change_quantity': quantity,
            'before_quantity': old_quantity,
            'after_quantity': inventory.quantity,
            'remark': remark,
            'created_by': created_by
        }
        
        if related_order:
            log_data['related_order_type'] = related_order.__class__.__name__
            log_data['related_order_id'] = related_order.id
        
        InventoryLog.objects.create(**log_data)
        
        return inventory
