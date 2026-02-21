"""
库存流水备注格式统一迁移脚本
将所有库存流水记录的备注格式统一为"类型 - 单号"格式
"""

from django.db import migrations


def update_inventory_log_remark(apps, schema_editor):
    """
    更新库存流水备注格式
    格式规范：类型 - 单号
    """
    InventoryLog = apps.get_model('inventory', 'InventoryLog')
    StockIn = apps.get_model('inventory', 'StockIn')
    StockOut = apps.get_model('inventory', 'StockOut')
    StockAdjust = apps.get_model('inventory', 'StockAdjust')
    StockTransfer = apps.get_model('inventory', 'StockTransfer')
    PurchaseOrder = apps.get_model('purchase', 'PurchaseOrder')
    SaleOrder = apps.get_model('sale', 'SaleOrder')
    
    updated_count = 0
    
    # 更新采购入库相关记录
    for stock_in in StockIn.objects.filter(purchase_order__isnull=False).select_related('purchase_order'):
        old_format1 = f'采购入库，单号：{stock_in.purchase_order.order_no}'
        new_format = f'采购入库 - {stock_in.purchase_order.order_no}'
        
        count = InventoryLog.objects.filter(
            related_order_type='StockIn',
            related_order_id=stock_in.id,
            remark=old_format1
        ).update(remark=new_format)
        updated_count += count
    
    # 更新销售出库相关记录
    for stock_out in StockOut.objects.filter(sale_order__isnull=False).select_related('sale_order'):
        old_format1 = f'销售出库，单号：{stock_out.sale_order.order_no}'
        new_format = f'销售出库 - {stock_out.sale_order.order_no}'
        
        count = InventoryLog.objects.filter(
            related_order_type='StockOut',
            related_order_id=stock_out.id,
            remark=old_format1
        ).update(remark=new_format)
        updated_count += count
    
    # 更新库存调整相关记录
    for adjust in StockAdjust.objects.all():
        old_format1 = f'库存调整，单号：{adjust.order_no}'
        old_format2 = f'库存调整-{adjust.order_no}'
        new_format = f'库存调整 - {adjust.order_no}'
        
        count = InventoryLog.objects.filter(
            related_order_type='StockAdjust',
            related_order_id=adjust.id,
            remark__in=[old_format1, old_format2]
        ).update(remark=new_format)
        updated_count += count
    
    # 更新库存调拨相关记录
    for transfer in StockTransfer.objects.all():
        old_format1_out = f'调拨出库，单号：{transfer.order_no}'
        old_format2_out = f'调拨出库-{transfer.order_no}'
        new_format_out = f'调拨出库 - {transfer.order_no}'
        
        old_format1_in = f'调拨入库，单号：{transfer.order_no}'
        old_format2_in = f'调拨入库-{transfer.order_no}'
        new_format_in = f'调拨入库 - {transfer.order_no}'
        
        count = InventoryLog.objects.filter(
            related_order_type='StockTransfer',
            related_order_id=transfer.id,
            remark__in=[old_format1_out, old_format2_out]
        ).update(remark=new_format_out)
        updated_count += count
        
        count = InventoryLog.objects.filter(
            related_order_type='StockTransfer',
            related_order_id=transfer.id,
            remark__in=[old_format1_in, old_format2_in]
        ).update(remark=new_format_in)
        updated_count += count
    
    print(f'库存流水备注格式迁移完成，共更新 {updated_count} 条记录')


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(update_inventory_log_remark, migrations.RunPython.noop),
    ]
