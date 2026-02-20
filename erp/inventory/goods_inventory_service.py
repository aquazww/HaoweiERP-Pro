"""
商品库存关联服务模块
实现商品信息与库存数据的关联、同步和一致性校验
"""
from django.db import transaction, models
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal


class GoodsInventoryService:
    """商品库存关联服务"""
    
    @staticmethod
    @transaction.atomic
    def on_goods_created(goods, warehouse_ids=None):
        """
        商品创建时的库存初始化
        :param goods: 商品对象
        :param warehouse_ids: 需要初始化的仓库ID列表，为空则初始化所有启用仓库
        """
        from inventory.models import Inventory
        from basic.models import Warehouse
        
        if warehouse_ids is None:
            warehouses = Warehouse.objects.filter(is_active=True)
        else:
            warehouses = Warehouse.objects.filter(id__in=warehouse_ids)
        
        inventories = []
        for warehouse in warehouses:
            inv, created = Inventory.objects.get_or_create(
                goods=goods,
                warehouse=warehouse,
                defaults={'quantity': Decimal('0')}
            )
            if created:
                inventories.append(inv)
        
        return inventories
    
    @staticmethod
    @transaction.atomic
    def on_goods_status_changed(goods, old_status, new_status):
        """
        商品状态变更处理
        :param goods: 商品对象
        :param old_status: 原状态
        :param new_status: 新状态
        """
        from inventory.models import Inventory
        
        if old_status == 1 and new_status == 0:
            Inventory.objects.filter(goods=goods).update(
                quantity=Decimal('0')
            )
        
        return True
    
    @staticmethod
    @transaction.atomic
    def on_goods_stock_threshold_changed(goods, old_min_stock=None, old_max_stock=None):
        """
        商品库存阈值变更处理
        :param goods: 商品对象
        :param old_min_stock: 原最低库存
        :param old_max_stock: 原最高库存
        """
        pass
    
    @staticmethod
    def get_goods_stock_status(goods):
        """
        获取商品库存状态
        :param goods: 商品对象
        :return: 库存状态字典
        """
        from inventory.models import Inventory
        
        total_quantity = Inventory.objects.filter(goods=goods).aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0')
        
        min_stock = goods.min_stock or 0
        max_stock = goods.max_stock or 0
        
        if total_quantity <= 0:
            status_code = 'out'
            status_text = '缺货'
        elif min_stock > 0 and total_quantity <= min_stock:
            status_code = 'low'
            status_text = '库存不足'
        elif max_stock > 0 and total_quantity >= max_stock:
            status_code = 'over'
            status_text = '库存过剩'
        else:
            status_code = 'normal'
            status_text = '正常'
        
        return {
            'total_quantity': total_quantity,
            'status_code': status_code,
            'status_text': status_text,
            'min_stock': min_stock,
            'max_stock': max_stock,
            'is_warning': status_code in ['out', 'low']
        }
    
    @staticmethod
    def get_goods_inventory_detail(goods):
        """
        获取商品在各仓库的库存详情
        :param goods: 商品对象
        :return: 库存详情列表
        """
        from inventory.models import Inventory
        
        inventories = Inventory.objects.filter(goods=goods).select_related('warehouse')
        
        result = []
        for inv in inventories:
            quantity = inv.quantity or Decimal('0')
            min_stock = goods.min_stock or 0
            max_stock = goods.max_stock or 0
            
            if quantity <= 0:
                status = 'out'
            elif min_stock > 0 and quantity <= min_stock:
                status = 'low'
            elif max_stock > 0 and quantity >= max_stock:
                status = 'over'
            else:
                status = 'normal'
            
            result.append({
                'warehouse_id': inv.warehouse.id,
                'warehouse_name': inv.warehouse.name,
                'quantity': quantity,
                'status': status,
                'updated_at': inv.updated_at
            })
        
        return result
    
    @staticmethod
    def check_consistency(goods_id=None):
        """
        数据一致性校验
        :param goods_id: 商品ID，为空则检查所有商品
        :return: 不一致数据列表
        """
        from inventory.models import Inventory, InventoryLog
        from basic.models import Goods
        
        inconsistencies = []
        
        if goods_id:
            goods_list = Goods.objects.filter(id=goods_id)
        else:
            goods_list = Goods.objects.all()
        
        for goods in goods_list:
            inventories = Inventory.objects.filter(goods=goods)
            
            for inv in inventories:
                logs = InventoryLog.objects.filter(
                    goods=goods,
                    warehouse=inv.warehouse
                ).order_by('created_at')
                
                calculated_quantity = Decimal('0')
                for log in logs:
                    if log.change_type in ['inbound', 'adjust']:
                        calculated_quantity += log.change_quantity
                    elif log.change_type == 'outbound':
                        calculated_quantity -= log.change_quantity
                
                if abs(inv.quantity - calculated_quantity) > Decimal('0.01'):
                    inconsistencies.append({
                        'type': 'quantity_mismatch',
                        'goods_id': goods.id,
                        'goods_name': goods.name,
                        'warehouse_id': inv.warehouse.id,
                        'warehouse_name': inv.warehouse.name,
                        'inventory_quantity': inv.quantity,
                        'calculated_quantity': calculated_quantity,
                        'difference': inv.quantity - calculated_quantity
                    })
        
        return inconsistencies
    
    @staticmethod
    @transaction.atomic
    def fix_inconsistency(inconsistency):
        """
        修复数据不一致
        :param inconsistency: 不一致数据字典
        """
        from inventory.models import Inventory
        
        try:
            inv = Inventory.objects.get(
                goods_id=inconsistency['goods_id'],
                warehouse_id=inconsistency['warehouse_id']
            )
            
            old_quantity = inv.quantity
            inv.quantity = inconsistency['calculated_quantity']
            inv.save()
            
            return {
                'success': True,
                'goods_id': inconsistency['goods_id'],
                'warehouse_id': inconsistency['warehouse_id'],
                'old_quantity': old_quantity,
                'new_quantity': inv.quantity
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_stock_warning_goods():
        """
        获取库存预警商品列表
        :return: 预警商品列表
        """
        from inventory.models import Inventory
        from basic.models import Goods
        
        warnings = []
        
        goods_list = Goods.objects.filter(status=1).prefetch_related('inventory_set')
        
        for goods in goods_list:
            stock_status = GoodsInventoryService.get_goods_stock_status(goods)
            
            if stock_status['is_warning']:
                warnings.append({
                    'goods_id': goods.id,
                    'goods_code': goods.code,
                    'goods_name': goods.name,
                    'category': goods.category.name if goods.category else '',
                    'total_quantity': stock_status['total_quantity'],
                    'min_stock': stock_status['min_stock'],
                    'max_stock': stock_status['max_stock'],
                    'status_code': stock_status['status_code'],
                    'status_text': stock_status['status_text']
                })
        
        return warnings
    
    @staticmethod
    def get_goods_stock_summary():
        """
        获取商品库存汇总统计
        :return: 统计数据
        """
        from inventory.models import Inventory
        from basic.models import Goods
        
        total_goods = Goods.objects.filter(status=1).count()
        
        total_quantity = Inventory.objects.aggregate(
            total=Sum('quantity')
        )['total'] or Decimal('0')
        
        out_of_stock = 0
        low_stock = 0
        normal_stock = 0
        over_stock = 0
        
        goods_list = Goods.objects.filter(status=1)
        for goods in goods_list:
            status = GoodsInventoryService.get_goods_stock_status(goods)
            if status['status_code'] == 'out':
                out_of_stock += 1
            elif status['status_code'] == 'low':
                low_stock += 1
            elif status['status_code'] == 'over':
                over_stock += 1
            else:
                normal_stock += 1
        
        return {
            'total_goods': total_goods,
            'total_quantity': total_quantity,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'normal_stock': normal_stock,
            'over_stock': over_stock,
            'warning_count': out_of_stock + low_stock
        }
