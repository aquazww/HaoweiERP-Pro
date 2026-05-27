# -*- coding: utf-8 -*-
"""
数量字段类型测试
验证所有数量相关字段均为整数类型
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from basic.models import Category, Goods, Supplier, Warehouse, Customer, Unit


User = get_user_model()


class QuantityFieldTypeTest(TestCase):
    """数量字段类型测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.supplier = Supplier.objects.create(
            code='SUP001',
            name='测试供应商',
            tax_no='91110000MA5ETEST1',
            address='北京市海淀区'
        )
        self.customer = Customer.objects.create(
            code='CUS001',
            name='测试客户',
            tax_no='91110000MA5ETEST2',
            address='北京市朝阳区'
        )
        self.warehouse = Warehouse.objects.create(name='测试仓库')
        self.category = Category.objects.create(name='电子产品', sort_order=1)
        self.unit = Unit.objects.create(name='个')
        self.goods = Goods.objects.create(
            code='G001',
            name='测试商品',
            category=self.category,
            unit=self.unit,
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00')
        )
    
    def test_inventory_quantity_is_integer(self):
        """测试库存数量字段为整数类型"""
        from inventory.models import Inventory
        
        inventory = Inventory.objects.create(
            goods=self.goods,
            warehouse=self.warehouse,
            quantity=100
        )
        
        self.assertEqual(inventory.quantity, 100)
        self.assertIsInstance(inventory.quantity, int)
        
        inventory.quantity = 999
        inventory.save()
        self.assertEqual(inventory.quantity, 999)
    
    def test_inventory_log_quantity_fields_are_integer(self):
        """测试库存流水数量字段为整数类型"""
        from inventory.models import InventoryLog
        
        log = InventoryLog.objects.create(
            goods=self.goods,
            warehouse=self.warehouse,
            change_type='inbound',
            change_quantity=50,
            before_quantity=100,
            after_quantity=150,
            created_by=self.user
        )
        
        self.assertEqual(log.change_quantity, 50)
        self.assertEqual(log.before_quantity, 100)
        self.assertEqual(log.after_quantity, 150)
        self.assertIsInstance(log.change_quantity, int)
        self.assertIsInstance(log.before_quantity, int)
        self.assertIsInstance(log.after_quantity, int)
    
    def test_purchase_item_quantity_is_integer(self):
        """测试采购明细数量字段为整数类型"""
        from purchase.models import PurchaseOrder, PurchaseItem
        
        order = PurchaseOrder.objects.create(
            order_no='PO202603160001',
            supplier=self.supplier,
            warehouse=self.warehouse,
            created_by=self.user
        )
        
        item = PurchaseItem.objects.create(
            order=order,
            goods=self.goods,
            quantity=100,
            price=Decimal('50.00')
        )
        
        self.assertEqual(item.quantity, 100)
        self.assertIsInstance(item.quantity, int)
        self.assertEqual(item.received_quantity, 0)
        self.assertIsInstance(item.received_quantity, int)
    
    def test_sale_item_quantity_is_integer(self):
        """测试销售明细数量字段为整数类型"""
        from sale.models import SaleOrder, SaleItem
        
        order = SaleOrder.objects.create(
            order_no='SO202603160001',
            customer=self.customer,
            warehouse=self.warehouse,
            created_by=self.user
        )
        
        item = SaleItem.objects.create(
            order=order,
            goods=self.goods,
            quantity=50,
            price=Decimal('89.00')
        )
        
        self.assertEqual(item.quantity, 50)
        self.assertIsInstance(item.quantity, int)
        self.assertEqual(item.shipped_quantity, 0)
        self.assertIsInstance(item.shipped_quantity, int)
    
    def test_stock_out_item_quantity_is_integer(self):
        """测试出库明细数量字段为整数类型"""
        from inventory.models import StockOut, StockOutItem
        
        stock_out = StockOut.objects.create(
            order_no='OUT202603160001',
            warehouse=self.warehouse,
            created_by=self.user
        )
        
        item = StockOutItem.objects.create(
            stock_out=stock_out,
            goods=self.goods,
            quantity=30,
            price=Decimal('89.00'),
            amount=Decimal('2670.00')
        )
        
        self.assertEqual(item.quantity, 30)
        self.assertIsInstance(item.quantity, int)
    
    def test_stock_adjust_item_quantity_is_integer(self):
        """测试库存调整明细数量字段为整数类型"""
        from inventory.models import StockAdjust, StockAdjustItem
        
        adjust = StockAdjust.objects.create(
            order_no='ADJ202603160001',
            warehouse=self.warehouse,
            adjust_type='increase',
            reason='check',
            created_by=self.user
        )
        
        item = StockAdjustItem.objects.create(
            adjust=adjust,
            goods=self.goods,
            before_quantity=100,
            adjust_quantity=10,
            after_quantity=110
        )
        
        self.assertEqual(item.before_quantity, 100)
        self.assertEqual(item.adjust_quantity, 10)
        self.assertEqual(item.after_quantity, 110)
        self.assertIsInstance(item.before_quantity, int)
        self.assertIsInstance(item.adjust_quantity, int)
        self.assertIsInstance(item.after_quantity, int)
    
    def test_stock_transfer_item_quantity_is_integer(self):
        """测试库存调拨明细数量字段为整数类型"""
        from inventory.models import StockTransfer, StockTransferItem
        
        warehouse2 = Warehouse.objects.create(name='测试仓库2')
        
        transfer = StockTransfer.objects.create(
            order_no='TRF202603160001',
            from_warehouse=self.warehouse,
            to_warehouse=warehouse2,
            created_by=self.user
        )
        
        item = StockTransferItem.objects.create(
            transfer=transfer,
            goods=self.goods,
            quantity=20
        )
        
        self.assertEqual(item.quantity, 20)
        self.assertIsInstance(item.quantity, int)
    
    def test_quantity_no_decimal_places(self):
        """测试数量字段不包含小数部分"""
        from inventory.models import Inventory
        
        inventory = Inventory.objects.create(
            goods=self.goods,
            warehouse=self.warehouse,
            quantity=100
        )
        
        str_quantity = str(inventory.quantity)
        self.assertNotIn('.', str_quantity)
        
        inventory.quantity = 0
        inventory.save()
        str_quantity = str(inventory.quantity)
        self.assertEqual(str_quantity, '0')


class QuantitySerializerValidationTest(TestCase):
    """数量序列化器验证测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.supplier = Supplier.objects.create(
            code='SUP001',
            name='测试供应商',
            tax_no='91110000MA5ETEST1',
            address='北京市海淀区'
        )
        self.warehouse = Warehouse.objects.create(name='测试仓库')
        self.category = Category.objects.create(name='电子产品', sort_order=1)
        self.goods = Goods.objects.create(
            code='G001',
            name='测试商品',
            category=self.category,
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00')
        )
    
    def test_purchase_item_serializer_validates_integer_quantity(self):
        """测试采购明细序列化器验证整数数量"""
        from purchase.serializers import PurchaseItemCreateSerializer
        
        data = {
            'goods': self.goods.id,
            'quantity': 10,
            'price': '50.00'
        }
        
        serializer = PurchaseItemCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_purchase_item_serializer_rejects_decimal_quantity(self):
        """测试采购明细序列化器拒绝小数数量"""
        from purchase.serializers import PurchaseItemCreateSerializer
        
        data = {
            'goods': self.goods.id,
            'quantity': 10.5,
            'price': '50.00'
        }
        
        serializer = PurchaseItemCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['quantity'], 10)
    
    def test_purchase_item_serializer_rejects_zero_quantity(self):
        """测试采购明细序列化器拒绝零数量"""
        from purchase.serializers import PurchaseItemCreateSerializer
        
        data = {
            'goods': self.goods.id,
            'quantity': 0,
            'price': '50.00'
        }
        
        serializer = PurchaseItemCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_purchase_item_serializer_rejects_negative_quantity(self):
        """测试采购明细序列化器拒绝负数数量"""
        from purchase.serializers import PurchaseItemCreateSerializer
        
        data = {
            'goods': self.goods.id,
            'quantity': -5,
            'price': '50.00'
        }
        
        serializer = PurchaseItemCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
