"""
采购订单模块测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from basic.models import Category, Goods, Supplier, Warehouse


User = get_user_model()


class PurchaseOrderModelTest(TestCase):
    """采购订单模型测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.supplier = Supplier.objects.create(
            code='SUP001',
            name='测试供应商',
            tax_no='91110000MA5ETEST1',
            address='北京市海淀区'
        )
        self.warehouse = Warehouse.objects.create(
            name='测试仓库'
        )
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1
        )
        self.goods = Goods.objects.create(
            code='G001',
            name='测试商品',
            category=self.category,
            unit='个',
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00')
        )
    
    def test_create_purchase_order(self):
        """测试创建采购订单"""
        from purchase.models import PurchaseOrder
        
        order = PurchaseOrder.objects.create(
            order_no='PO202602200001',
            supplier=self.supplier,
            warehouse=self.warehouse,
            total_amount=Decimal('1000.00'),
            status='pending'
        )
        
        self.assertEqual(order.order_no, 'PO202602200001')
        self.assertEqual(order.supplier, self.supplier)
        self.assertEqual(order.warehouse, self.warehouse)
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.created_at)
    
    def test_create_purchase_item(self):
        """测试创建采购明细"""
        from purchase.models import PurchaseOrder, PurchaseItem
        
        order = PurchaseOrder.objects.create(
            order_no='PO202602200002',
            supplier=self.supplier,
            warehouse=self.warehouse
        )
        
        item = PurchaseItem.objects.create(
            order=order,
            goods=self.goods,
            quantity=Decimal('10.00'),
            price=Decimal('50.00')
        )
        
        self.assertEqual(item.order, order)
        self.assertEqual(item.goods, self.goods)
        self.assertEqual(item.quantity, Decimal('10.00'))
        self.assertEqual(item.price, Decimal('50.00'))
        self.assertEqual(item.amount, Decimal('500.00'))
    
    def test_purchase_item_unique_constraint(self):
        """测试采购明细商品唯一性约束"""
        from purchase.models import PurchaseOrder, PurchaseItem
        from django.db import IntegrityError
        
        order = PurchaseOrder.objects.create(
            order_no='PO202602200003',
            supplier=self.supplier,
            warehouse=self.warehouse
        )
        
        PurchaseItem.objects.create(
            order=order,
            goods=self.goods,
            quantity=Decimal('10.00'),
            price=Decimal('50.00')
        )
        
        with self.assertRaises(IntegrityError):
            PurchaseItem.objects.create(
                order=order,
                goods=self.goods,
                quantity=Decimal('5.00'),
                price=Decimal('45.00')
            )


class PurchaseOrderAPITest(TestCase):
    """采购订单API测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.client = APIClient()
        
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
        self.warehouse = Warehouse.objects.create(
            name='测试仓库'
        )
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1
        )
        self.goods1 = Goods.objects.create(
            code='G001',
            name='测试商品1',
            category=self.category,
            unit='个',
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00')
        )
        self.goods2 = Goods.objects.create(
            code='G002',
            name='测试商品2',
            category=self.category,
            unit='件',
            purchase_price=Decimal('100.00'),
            sale_price=Decimal('150.00')
        )
    
    def test_list_orders_unauthenticated(self):
        """测试未认证用户访问采购订单列表"""
        response = self.client.get('/api/v1/purchase/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_orders_authenticated(self):
        """测试认证用户访问采购订单列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/purchase/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_order_success(self):
        """测试成功创建采购订单"""
        from purchase.models import PurchaseOrder
        
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods1.id,
                    'quantity': '10.00',
                    'price': '50.00'
                },
                {
                    'goods': self.goods2.id,
                    'quantity': '5.00',
                    'price': '100.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], '创建成功')
        
        order = PurchaseOrder.objects.get(order_no__startswith='PO')
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_amount, Decimal('1000.00'))
    
    def test_create_order_missing_required_fields(self):
        """测试创建采购订单缺少必填字段"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_empty_items(self):
        """测试创建采购订单明细为空"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': []
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_duplicate_goods(self):
        """测试创建采购订单商品重复"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods1.id,
                    'quantity': '10.00',
                    'price': '50.00'
                },
                {
                    'goods': self.goods1.id,
                    'quantity': '5.00',
                    'price': '45.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_invalid_quantity(self):
        """测试创建采购订单数量无效"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods1.id,
                    'quantity': '0',
                    'price': '50.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_invalid_price(self):
        """测试创建采购订单单价无效"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods1.id,
                    'quantity': '10.00',
                    'price': '0'
                }
            ]
        }
        
        response = self.client.post('/api/v1/purchase/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PurchaseOrderSerializerTest(TestCase):
    """采购订单序列化器测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.supplier = Supplier.objects.create(
            code='SUP001',
            name='测试供应商',
            tax_no='91110000MA5ETEST1',
            address='北京市海淀区'
        )
        self.warehouse = Warehouse.objects.create(
            name='测试仓库'
        )
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1
        )
        self.goods = Goods.objects.create(
            code='G001',
            name='测试商品',
            category=self.category,
            unit='个',
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00')
        )
    
    def test_serializer_valid_data(self):
        """测试序列化器有效数据"""
        from purchase.serializers import PurchaseOrderCreateSerializer
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods.id,
                    'quantity': '10.00',
                    'price': '50.00'
                }
            ]
        }
        
        serializer = PurchaseOrderCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_supplier(self):
        """测试序列化器缺少供应商"""
        from purchase.serializers import PurchaseOrderCreateSerializer
        
        data = {
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods.id,
                    'quantity': '10.00',
                    'price': '50.00'
                }
            ]
        }
        
        serializer = PurchaseOrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_missing_items(self):
        """测试序列化器缺少明细"""
        from purchase.serializers import PurchaseOrderCreateSerializer
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': []
        }
        
        serializer = PurchaseOrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('items', serializer.errors)
    
    def test_serializer_invalid_quantity(self):
        """测试序列化器数量无效"""
        from purchase.serializers import PurchaseOrderCreateSerializer
        
        data = {
            'supplier': self.supplier.id,
            'warehouse': self.warehouse.id,
            'order_date': '2026-02-20',
            'items': [
                {
                    'goods': self.goods.id,
                    'quantity': '-10.00',
                    'price': '50.00'
                }
            ]
        }
        
        serializer = PurchaseOrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
