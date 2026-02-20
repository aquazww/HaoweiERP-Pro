"""
商品管理模块测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from basic.models import Category, Goods, Supplier


User = get_user_model()


class GoodsModelTest(TestCase):
    """商品模型测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1,
            is_active=True
        )
    
    def test_create_goods(self):
        """测试创建商品"""
        goods = Goods.objects.create(
            code='TEST001',
            name='测试商品',
            category=self.category,
            unit='个',
            purchase_price=Decimal('50.00'),
            sale_price=Decimal('89.00'),
            retail_price=Decimal('99.00'),
            status=1
        )
        
        self.assertEqual(goods.code, 'TEST001')
        self.assertEqual(goods.name, '测试商品')
        self.assertEqual(goods.category, self.category)
        self.assertEqual(goods.unit, '个')
        self.assertEqual(goods.purchase_price, Decimal('50.00'))
        self.assertEqual(goods.sale_price, Decimal('89.00'))
        self.assertEqual(goods.status, 1)
        self.assertIsNotNone(goods.created_at)
        self.assertIsNotNone(goods.updated_at)
    
    def test_goods_str(self):
        """测试商品字符串表示"""
        goods = Goods.objects.create(
            code='TEST002',
            name='测试商品2',
            category=self.category,
            unit='个'
        )
        self.assertEqual(str(goods), 'TEST002 - 测试商品2')
    
    def test_goods_code_unique(self):
        """测试商品编码唯一性"""
        Goods.objects.create(
            code='UNIQUE001',
            name='商品1',
            category=self.category,
            unit='个'
        )
        
        with self.assertRaises(Exception):
            Goods.objects.create(
                code='UNIQUE001',
                name='商品2',
                category=self.category,
                unit='个'
            )


class GoodsAPITest(TestCase):
    """商品API测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1,
            is_active=True
        )
        
        self.goods = Goods.objects.create(
            code='API001',
            name='API测试商品',
            category=self.category,
            unit='个',
            purchase_price=Decimal('100.00'),
            sale_price=Decimal('150.00'),
            status=1
        )
    
    def test_list_goods_unauthenticated(self):
        """测试未认证用户访问商品列表"""
        response = self.client.get('/api/v1/basic/goods/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_goods_authenticated(self):
        """测试认证用户访问商品列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/basic/goods/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_goods_success(self):
        """测试成功创建商品"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEW001',
            'name': '新商品',
            'category': self.category.id,
            'unit': '件',
            'purchase_price': '50.00',
            'sale_price': '89.00',
            'retail_price': '99.00',
            'min_stock': 10,
            'max_stock': 100,
            'status': 1
        }
        
        response = self.client.post('/api/v1/basic/goods/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], '创建成功')
    
    def test_create_goods_missing_required_fields(self):
        """测试创建商品缺少必填字段"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEW002',
        }
        
        response = self.client.post('/api/v1/basic/goods/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_goods_sale_price_lower_than_purchase(self):
        """测试销售价低于进货价"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'PRICE001',
            'name': '价格测试商品',
            'category': self.category.id,
            'unit': '个',
            'purchase_price': '100.00',
            'sale_price': '50.00'
        }
        
        response = self.client.post('/api/v1/basic/goods/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_goods_max_stock_lower_than_min(self):
        """测试最高库存低于最低库存"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'STOCK001',
            'name': '库存测试商品',
            'category': self.category.id,
            'unit': '个',
            'min_stock': 100,
            'max_stock': 50
        }
        
        response = self.client.post('/api/v1/basic/goods/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_goods_success(self):
        """测试成功更新商品"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': self.goods.code,
            'name': '更新后的商品名',
            'category': self.category.id,
            'unit': '个',
            'purchase_price': '120.00',
            'sale_price': '180.00',
            'status': 1
        }
        
        response = self.client.put(f'/api/v1/basic/goods/{self.goods.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '更新后的商品名')
    
    def test_delete_goods_success(self):
        """测试成功删除商品"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/v1/basic/goods/{self.goods.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        with self.assertRaises(Goods.DoesNotExist):
            Goods.objects.get(id=self.goods.id)
    
    def test_search_goods(self):
        """测试搜索商品"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/basic/goods/', {'search': 'API'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['items']), 1)


class GoodsSerializerTest(TestCase):
    """商品序列化器测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.category = Category.objects.create(
            name='电子产品',
            sort_order=1,
            is_active=True
        )
    
    def test_serializer_valid_data(self):
        """测试序列化器有效数据"""
        from basic.serializers import GoodsSerializer
        
        data = {
            'code': 'SER001',
            'name': '序列化测试商品',
            'category': self.category.id,
            'unit': '个',
            'purchase_price': '50.00',
            'sale_price': '89.00'
        }
        
        serializer = GoodsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_invalid_code_empty(self):
        """测试序列化器编码为空"""
        from basic.serializers import GoodsSerializer
        
        data = {
            'code': '',
            'name': '测试商品',
            'category': self.category.id,
            'unit': '个'
        }
        
        serializer = GoodsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_serializer_invalid_name_too_long(self):
        """测试序列化器名称过长"""
        from basic.serializers import GoodsSerializer
        
        data = {
            'code': 'LONG001',
            'name': 'A' * 101,
            'category': self.category.id,
            'unit': '个'
        }
        
        serializer = GoodsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_serializer_negative_price(self):
        """测试序列化器负价格"""
        from basic.serializers import GoodsSerializer
        
        data = {
            'code': 'NEG001',
            'name': '负价格测试',
            'category': self.category.id,
            'unit': '个',
            'purchase_price': '-10.00'
        }
        
        serializer = GoodsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purchase_price', serializer.errors)


class SupplierModelTest(TestCase):
    """供应商模型测试"""
    
    def test_create_supplier(self):
        """测试创建供应商"""
        supplier = Supplier.objects.create(
            code='SUP001',
            name='测试供应商',
            tax_no='91110000MA5EXXXXX',
            address='北京市海淀区',
            contact='张三',
            phone='13800138000',
            email='test@supplier.com',
            bank_name='中国银行',
            bank_account='1234567890',
            status=1
        )
        
        self.assertEqual(supplier.code, 'SUP001')
        self.assertEqual(supplier.name, '测试供应商')
        self.assertEqual(supplier.tax_no, '91110000MA5EXXXXX')
        self.assertEqual(supplier.address, '北京市海淀区')
        self.assertEqual(supplier.contact, '张三')
        self.assertEqual(supplier.phone, '13800138000')
        self.assertEqual(supplier.email, 'test@supplier.com')
        self.assertEqual(supplier.status, 1)
        self.assertIsNotNone(supplier.created_at)
        self.assertIsNotNone(supplier.updated_at)
    
    def test_supplier_str(self):
        """测试供应商字符串表示"""
        supplier = Supplier.objects.create(
            code='SUP002',
            name='测试供应商2',
            tax_no='91110000MA5EXXXX2',
            address='上海市'
        )
        self.assertEqual(str(supplier), 'SUP002 - 测试供应商2')
    
    def test_supplier_code_unique(self):
        """测试供应商编码唯一性"""
        Supplier.objects.create(
            code='UNIQUE001',
            name='供应商1',
            tax_no='91110000MA5EXXXX1',
            address='地址1'
        )
        
        with self.assertRaises(Exception):
            Supplier.objects.create(
                code='UNIQUE001',
                name='供应商2',
                tax_no='91110000MA5EXXXX2',
                address='地址2'
            )


class SupplierAPITest(TestCase):
    """供应商API测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            code='API001',
            name='API测试供应商',
            tax_no='91110000MA5EAPI01',
            address='北京市海淀区',
            contact='李四',
            phone='13900139000',
            status=1
        )
    
    def test_list_suppliers_unauthenticated(self):
        """测试未认证用户访问供应商列表"""
        response = self.client.get('/api/v1/basic/suppliers/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_suppliers_authenticated(self):
        """测试认证用户访问供应商列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/basic/suppliers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_supplier_success(self):
        """测试成功创建供应商"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEWSUP001',
            'name': '新供应商',
            'tax_no': '91110000MA5ENEW01',
            'address': '深圳市南山区',
            'contact': '王五',
            'phone': '13700137000',
            'email': 'new@supplier.com',
            'bank_name': '工商银行',
            'bank_account': '9876543210',
            'status': 1
        }
        
        response = self.client.post('/api/v1/basic/suppliers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], '创建成功')
    
    def test_create_supplier_missing_required_fields(self):
        """测试创建供应商缺少必填字段"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEWSUP002',
        }
        
        response = self.client.post('/api/v1/basic/suppliers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_supplier_invalid_email(self):
        """测试创建供应商无效邮箱"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'EMAIL001',
            'name': '邮箱测试供应商',
            'tax_no': '91110000MA5EEMAI1',
            'address': '广州市',
            'email': 'invalid-email'
        }
        
        response = self.client.post('/api/v1/basic/suppliers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_supplier_negative_balance(self):
        """测试创建供应商负余额"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'BALANCE001',
            'name': '余额测试供应商',
            'tax_no': '91110000MA5EBALA1',
            'address': '杭州市',
            'balance': '-1000.00'
        }
        
        response = self.client.post('/api/v1/basic/suppliers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_supplier_success(self):
        """测试成功更新供应商"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': self.supplier.code,
            'name': '更新后的供应商名',
            'tax_no': self.supplier.tax_no,
            'address': '上海市浦东新区',
            'status': 1
        }
        
        response = self.client.put(f'/api/v1/basic/suppliers/{self.supplier.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '更新后的供应商名')
    
    def test_delete_supplier_success(self):
        """测试成功删除供应商"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/v1/basic/suppliers/{self.supplier.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        with self.assertRaises(Supplier.DoesNotExist):
            Supplier.objects.get(id=self.supplier.id)
    
    def test_search_suppliers(self):
        """测试搜索供应商"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/basic/suppliers/', {'search': 'API'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['items']), 1)
    
    def test_filter_suppliers_by_status(self):
        """测试按状态筛选供应商"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/basic/suppliers/', {'status': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SupplierSerializerTest(TestCase):
    """供应商序列化器测试"""
    
    def test_serializer_valid_data(self):
        """测试序列化器有效数据"""
        from basic.serializers import SupplierSerializer
        
        data = {
            'code': 'SER001',
            'name': '序列化测试供应商',
            'tax_no': '91110000MA5ESER01',
            'address': '深圳市南山区',
            'contact': '测试联系人',
            'phone': '13800138000',
            'email': 'test@supplier.com'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_invalid_code_empty(self):
        """测试序列化器编码为空"""
        from basic.serializers import SupplierSerializer
        
        data = {
            'code': '',
            'name': '测试供应商',
            'tax_no': '91110000MA5ETEST1',
            'address': '北京市'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_serializer_invalid_name_too_long(self):
        """测试序列化器名称过长"""
        from basic.serializers import SupplierSerializer
        
        data = {
            'code': 'LONG001',
            'name': 'A' * 101,
            'tax_no': '91110000MA5ELONG1',
            'address': '北京市'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_serializer_invalid_email(self):
        """测试序列化器无效邮箱"""
        from basic.serializers import SupplierSerializer
        
        data = {
            'code': 'EMAIL001',
            'name': '邮箱测试供应商',
            'tax_no': '91110000MA5EEMAI1',
            'address': '北京市',
            'email': 'invalid-email'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_serializer_negative_balance(self):
        """测试序列化器负余额"""
        from basic.serializers import SupplierSerializer
        
        data = {
            'code': 'NEG001',
            'name': '负余额测试',
            'tax_no': '91110000MA5ENEG01',
            'address': '北京市',
            'balance': '-100.00'
        }
        
        serializer = SupplierSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('balance', serializer.errors)


class CustomerModelTest(TestCase):
    """客户模型测试"""
    
    def test_create_customer(self):
        """测试创建客户"""
        from basic.models import Customer
        customer = Customer.objects.create(
            code='CUS001',
            name='测试客户公司',
            tax_no='91110000MA5ECUS01',
            address='北京市朝阳区',
            contact='王经理',
            phone='13800138001',
            email='test@customer.com',
            bank_name='建设银行',
            bank_account='1234567891',
            status=1
        )
        
        self.assertEqual(customer.code, 'CUS001')
        self.assertEqual(customer.name, '测试客户公司')
        self.assertEqual(customer.tax_no, '91110000MA5ECUS01')
        self.assertEqual(customer.address, '北京市朝阳区')
        self.assertEqual(customer.contact, '王经理')
        self.assertEqual(customer.phone, '13800138001')
        self.assertEqual(customer.email, 'test@customer.com')
        self.assertEqual(customer.status, 1)
        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)
    
    def test_customer_str(self):
        """测试客户字符串表示"""
        from basic.models import Customer
        customer = Customer.objects.create(
            code='CUS002',
            name='测试客户公司2',
            tax_no='91110000MA5ECUS02',
            address='上海市'
        )
        self.assertEqual(str(customer), 'CUS002 - 测试客户公司2')
    
    def test_customer_code_unique(self):
        """测试客户编码唯一性"""
        from basic.models import Customer
        Customer.objects.create(
            code='UNIQUECUS001',
            name='客户1',
            tax_no='91110000MA5ECUS1',
            address='地址1'
        )
        
        with self.assertRaises(Exception):
            Customer.objects.create(
                code='UNIQUECUS001',
                name='客户2',
                tax_no='91110000MA5ECUS2',
                address='地址2'
            )


class CustomerAPITest(TestCase):
    """客户API测试"""
    
    def setUp(self):
        """测试数据准备"""
        from basic.models import Customer
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.customer = Customer.objects.create(
            code='APICUS001',
            name='API测试客户',
            tax_no='91110000MA5EAPI01',
            address='北京市朝阳区',
            contact='李总',
            phone='13900139001',
            status=1
        )
    
    def test_list_customers_unauthenticated(self):
        """测试未认证用户访问客户列表"""
        response = self.client.get('/api/v1/basic/customers/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_customers_authenticated(self):
        """测试认证用户访问客户列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/basic/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_customer_success(self):
        """测试成功创建客户"""
        from basic.models import Customer
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEWCUS001',
            'name': '新客户公司',
            'tax_no': '91110000MA5ENEW01',
            'address': '深圳市福田区',
            'contact': '赵总',
            'phone': '13700137001',
            'email': 'new@customer.com',
            'bank_name': '招商银行',
            'bank_account': '9876543211',
            'status': 1
        }
        
        response = self.client.post('/api/v1/basic/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], '创建成功')
    
    def test_create_customer_missing_required_fields(self):
        """测试创建客户缺少必填字段"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'NEWCUS002',
        }
        
        response = self.client.post('/api/v1/basic/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_customer_invalid_email(self):
        """测试创建客户无效邮箱"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'EMAILCUS001',
            'name': '邮箱测试客户',
            'tax_no': '91110000MA5EEMAI1',
            'address': '广州市',
            'email': 'invalid-email'
        }
        
        response = self.client.post('/api/v1/basic/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_customer_negative_balance(self):
        """测试创建客户负余额"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': 'BALANCECUS001',
            'name': '余额测试客户',
            'tax_no': '91110000MA5EBALA1',
            'address': '杭州市',
            'balance': '-1000.00'
        }
        
        response = self.client.post('/api/v1/basic/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_customer_success(self):
        """测试成功更新客户"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'code': self.customer.code,
            'name': '更新后的客户名',
            'tax_no': self.customer.tax_no,
            'address': '上海市浦东新区',
            'status': 1
        }
        
        response = self.client.put(f'/api/v1/basic/customers/{self.customer.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '更新后的客户名')
    
    def test_delete_customer_success(self):
        """测试成功删除客户"""
        from basic.models import Customer
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/v1/basic/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        with self.assertRaises(Customer.DoesNotExist):
            Customer.objects.get(id=self.customer.id)
    
    def test_search_customers(self):
        """测试搜索客户"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/basic/customers/', {'search': 'API'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['items']), 1)
    
    def test_filter_customers_by_status(self):
        """测试按状态筛选客户"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/basic/customers/', {'status': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomerSerializerTest(TestCase):
    """客户序列化器测试"""
    
    def test_serializer_valid_data(self):
        """测试序列化器有效数据"""
        from basic.serializers import CustomerSerializer
        
        data = {
            'code': 'SERCUS001',
            'name': '序列化测试客户',
            'tax_no': '91110000MA5ESER01',
            'address': '深圳市南山区',
            'contact': '测试联系人',
            'phone': '13800138000',
            'email': 'test@customer.com'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_invalid_code_empty(self):
        """测试序列化器编码为空"""
        from basic.serializers import CustomerSerializer
        
        data = {
            'code': '',
            'name': '测试客户',
            'tax_no': '91110000MA5ETEST1',
            'address': '北京市'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_serializer_invalid_name_too_long(self):
        """测试序列化器名称过长"""
        from basic.serializers import CustomerSerializer
        
        data = {
            'code': 'LONGCUS001',
            'name': 'A' * 101,
            'tax_no': '91110000MA5ELONG1',
            'address': '北京市'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_serializer_invalid_email(self):
        """测试序列化器无效邮箱"""
        from basic.serializers import CustomerSerializer
        
        data = {
            'code': 'EMAILCUS001',
            'name': '邮箱测试客户',
            'tax_no': '91110000MA5EEMAI1',
            'address': '北京市',
            'email': 'invalid-email'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_serializer_negative_balance(self):
        """测试序列化器负余额"""
        from basic.serializers import CustomerSerializer
        
        data = {
            'code': 'NEGCUS001',
            'name': '负余额测试',
            'tax_no': '91110000MA5ENEG01',
            'address': '北京市',
            'balance': '-100.00'
        }
        
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('balance', serializer.errors)
