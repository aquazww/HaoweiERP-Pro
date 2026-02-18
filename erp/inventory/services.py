from django.db import transaction
from .models import Inventory, InventoryLog


class InventoryService:
    """库存服务类"""

    @staticmethod
    @transaction.atomic
    def stock_in(goods, warehouse, quantity, related_order=None, remark=''):
        """
        入库操作
        """
        # 获取或创建库存记录
        inventory, created = Inventory.objects.get_or_create(
            goods=goods,
            warehouse=warehouse,
            defaults={'quantity': 0}
        )
        
        # 更新库存数量
        old_quantity = inventory.quantity
        inventory.quantity += quantity
        inventory.save()
        
        # 记录库存流水
        InventoryLog.objects.create(
            goods=goods,
            warehouse=warehouse,
            change_type='in',
            change_quantity=quantity,
            before_quantity=old_quantity,
            after_quantity=inventory.quantity,
            related_order=related_order,
            remark=remark
        )
        
        return inventory

    @staticmethod
    @transaction.atomic
    def stock_out(goods, warehouse, quantity, related_order=None, remark=''):
        """
        出库操作
        """
        # 获取库存记录
        try:
            inventory = Inventory.objects.get(
                goods=goods,
                warehouse=warehouse
            )
        except Inventory.DoesNotExist:
            raise ValueError(f'商品 {goods.name} 在该仓库无库存')
        
        # 检查库存是否足够
        if inventory.quantity < quantity:
            raise ValueError(f'商品 {goods.name} 库存不足，当前库存：{inventory.quantity}')
        
        # 更新库存数量
        old_quantity = inventory.quantity
        inventory.quantity -= quantity
        inventory.save()
        
        # 记录库存流水
        InventoryLog.objects.create(
            goods=goods,
            warehouse=warehouse,
            change_type='out',
            change_quantity=quantity,
            before_quantity=old_quantity,
            after_quantity=inventory.quantity,
            related_order=related_order,
            remark=remark
        )
        
        return inventory
