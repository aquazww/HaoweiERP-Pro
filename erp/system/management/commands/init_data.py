"""
初始化基础数据的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from basic.models import Category, Warehouse, Supplier, Customer, Goods
from system.models import Role
from decimal import Decimal


class Command(BaseCommand):
    help = '初始化系统基础数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化基础数据...')
        
        # 1. 创建角色
        self.create_roles()
        
        # 2. 创建管理员用户
        self.create_admin_user()
        
        # 3. 创建仓库
        self.create_warehouses()
        
        # 4. 创建商品分类
        self.create_categories()
        
        # 5. 创建供应商
        self.create_suppliers()
        
        # 6. 创建客户
        self.create_customers()
        
        # 7. 创建商品
        self.create_goods()
        
        self.stdout.write(self.style.SUCCESS('基础数据初始化完成！'))

    def create_roles(self):
        """创建角色"""
        roles_data = [
            {
                'name': '管理员',
                'description': '系统管理员，拥有所有权限',
                'permissions': {
                    'basic': True, 'purchase': True, 'sale': True,
                    'inventory': True, 'finance': True, 'reports': True, 'system': True
                }
            },
            {
                'name': '销售员',
                'description': '销售人员，负责销售管理',
                'permissions': {
                    'basic': True, 'sale': True, 'inventory': True, 'reports': True
                }
            },
            {
                'name': '采购员',
                'description': '采购人员，负责采购管理',
                'permissions': {
                    'basic': True, 'purchase': True, 'inventory': True, 'reports': True
                }
            },
            {
                'name': '仓管员',
                'description': '仓库管理人员，负责库存管理',
                'permissions': {
                    'basic': True, 'inventory': True, 'reports': True
                }
            },
            {
                'name': '财务员',
                'description': '财务人员，负责财务管理',
                'permissions': {
                    'basic': True, 'finance': True, 'reports': True
                }
            },
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'  创建角色: {role.name}')
            else:
                self.stdout.write(f'  角色已存在: {role.name}')

    def create_admin_user(self):
        """创建管理员用户"""
        User = get_user_model()
        
        # 获取管理员角色
        admin_role = Role.objects.filter(name='管理员').first()
        
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@haowei.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': admin_role
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('  创建管理员用户: admin (密码: admin123)')
        else:
            self.stdout.write('  管理员用户已存在: admin')

    def create_warehouses(self):
        """创建仓库"""
        warehouses_data = [
            {'name': '主仓库', 'address': '公司总部', 'contact': '张三', 'phone': '13800138001'},
            {'name': '备用仓库', 'address': '分公司', 'contact': '李四', 'phone': '13800138002'},
        ]
        
        for wh_data in warehouses_data:
            warehouse, created = Warehouse.objects.get_or_create(
                name=wh_data['name'],
                defaults=wh_data
            )
            if created:
                self.stdout.write(f'  创建仓库: {warehouse.name}')
            else:
                self.stdout.write(f'  仓库已存在: {warehouse.name}')

    def create_categories(self):
        """创建商品分类"""
        categories_data = [
            {'name': '电子产品', 'sort_order': 1},
            {'name': '办公用品', 'sort_order': 2},
            {'name': '日用品', 'sort_order': 3},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  创建分类: {category.name}')
            else:
                self.stdout.write(f'  分类已存在: {category.name}')

    def create_suppliers(self):
        """创建供应商"""
        suppliers_data = [
            {
                'code': 'SUP001',
                'name': '深圳电子科技有限公司',
                'tax_no': '91440300MA5EXXXXX',
                'address': '深圳市南山区科技园',
                'contact': '王经理',
                'phone': '0755-12345678',
                'email': 'sales@sz-electronics.com',
                'bank_name': '中国工商银行深圳分行',
                'bank_account': '4000 0123 4567 8901',
            },
            {
                'code': 'SUP002',
                'name': '广州办公用品供应商',
                'tax_no': '91440100MA5EXXXXX',
                'address': '广州市天河区',
                'contact': '陈经理',
                'phone': '020-87654321',
                'email': 'sales@gz-office.com',
                'bank_name': '中国建设银行广州分行',
                'bank_account': '4400 0123 4567 8902',
            },
        ]
        
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                code=sup_data['code'],
                defaults=sup_data
            )
            if created:
                self.stdout.write(f'  创建供应商: {supplier.name}')
            else:
                self.stdout.write(f'  供应商已存在: {supplier.name}')

    def create_customers(self):
        """创建客户"""
        customers_data = [
            {
                'code': 'CUS001',
                'name': '北京科技有限公司',
                'tax_no': '91110000MA5EXXXXX',
                'address': '北京市海淀区中关村',
                'contact': '刘总',
                'phone': '010-12345678',
                'email': 'purchase@bj-tech.com',
                'bank_name': '中国银行北京分行',
                'bank_account': '1100 0123 4567 8903',
            },
            {
                'code': 'CUS002',
                'name': '上海贸易公司',
                'tax_no': '91310000MA5EXXXXX',
                'address': '上海市浦东新区',
                'contact': '赵经理',
                'phone': '021-87654321',
                'email': 'trade@sh-trade.com',
                'bank_name': '中国农业银行上海分行',
                'bank_account': '3100 0123 4567 8904',
            },
        ]
        
        for cus_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                code=cus_data['code'],
                defaults=cus_data
            )
            if created:
                self.stdout.write(f'  创建客户: {customer.name}')
            else:
                self.stdout.write(f'  客户已存在: {customer.name}')

    def create_goods(self):
        """创建商品"""
        # 获取分类
        electronics = Category.objects.filter(name='电子产品').first()
        office = Category.objects.filter(name='办公用品').first()
        
        goods_data = [
            {
                'code': 'G001',
                'name': '无线鼠标',
                'category': electronics,
                'unit': '个',
                'spec': '黑色/无线',
                'purchase_price': Decimal('50.00'),
                'sale_price': Decimal('89.00'),
                'retail_price': Decimal('99.00'),
            },
            {
                'code': 'G002',
                'name': '机械键盘',
                'category': electronics,
                'unit': '个',
                'spec': '青轴/RGB背光',
                'purchase_price': Decimal('150.00'),
                'sale_price': Decimal('299.00'),
                'retail_price': Decimal('349.00'),
            },
            {
                'code': 'G003',
                'name': '27英寸显示器',
                'category': electronics,
                'unit': '台',
                'spec': '2K/IPS',
                'purchase_price': Decimal('800.00'),
                'sale_price': Decimal('1299.00'),
                'retail_price': Decimal('1499.00'),
            },
            {
                'code': 'G004',
                'name': 'A4打印纸',
                'category': office,
                'unit': '包',
                'spec': '500张/包',
                'purchase_price': Decimal('20.00'),
                'sale_price': Decimal('35.00'),
                'retail_price': Decimal('40.00'),
            },
            {
                'code': 'G005',
                'name': '签字笔',
                'category': office,
                'unit': '盒',
                'spec': '12支/盒',
                'purchase_price': Decimal('8.00'),
                'sale_price': Decimal('15.00'),
                'retail_price': Decimal('18.00'),
            },
        ]
        
        for goods_data in goods_data:
            goods, created = Goods.objects.get_or_create(
                code=goods_data['code'],
                defaults=goods_data
            )
            if created:
                self.stdout.write(f'  创建商品: {goods.name}')
            else:
                self.stdout.write(f'  商品已存在: {goods.name}')
