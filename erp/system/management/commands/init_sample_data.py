from django.core.management.base import BaseCommand
from basic.models import Category, Warehouse, Supplier, Customer, Goods


class Command(BaseCommand):
    help = '初始化示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化示例数据...')

        category1, _ = Category.objects.get_or_create(
            name='食品饮料',
            defaults={'sort_order': 1}
        )
        category2, _ = Category.objects.get_or_create(
            name='日用百货',
            defaults={'sort_order': 2}
        )
        self.stdout.write(f'商品分类已创建/已存在')

        warehouse, _ = Warehouse.objects.get_or_create(
            name='主仓库',
            defaults={
                'address': '北京市朝阳区',
                'contact': '张经理',
                'phone': '13800138000'
            }
        )
        self.stdout.write(f'仓库已创建/已存在')

        supplier, _ = Supplier.objects.get_or_create(
            code='S001',
            defaults={
                'name': '北京供应商有限公司',
                'tax_no': '91110000123456789A',
                'address': '北京市海淀区中关村大街1号',
                'contact': '李总',
                'phone': '13900139000',
                'email': 'contact@beijingsupplier.com',
                'bank_name': '中国工商银行北京分行',
                'bank_account': '6222021234567890123',
                'bank_branch_no': '102100000000',
                'remark': '长期合作供应商',
                'status': 1
            }
        )
        self.stdout.write(f'供应商已创建/已存在')

        customer, _ = Customer.objects.get_or_create(
            code='C001',
            defaults={
                'name': '北京客户有限公司',
                'tax_no': '91110000987654321B',
                'address': '北京市西城区金融街1号',
                'contact': '王总',
                'phone': '13700137000',
                'email': 'contact@beijingcustomer.com',
                'bank_name': '中国建设银行北京分行',
                'bank_account': '6217001234567890456',
                'bank_branch_no': '105100000000',
                'remark': '重要客户',
                'status': 1
            }
        )
        self.stdout.write(f'客户已创建/已存在')

        goods_data = [
            {'code': 'G001', 'name': '矿泉水', 'category': category1, 'unit': '瓶', 'purchase_price': 1.0, 'sale_price': 2.0},
            {'code': 'G002', 'name': '面包', 'category': category1, 'unit': '个', 'purchase_price': 3.0, 'sale_price': 5.0},
            {'code': 'G003', 'name': '毛巾', 'category': category2, 'unit': '条', 'purchase_price': 5.0, 'sale_price': 10.0},
        ]

        for data in goods_data:
            Goods.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
        self.stdout.write(f'商品已创建/已存在')

        self.stdout.write(self.style.SUCCESS('示例数据初始化完成！'))
