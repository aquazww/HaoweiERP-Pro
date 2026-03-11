"""
初始化销售出库单示例数据的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from basic.models import Warehouse, Goods, Customer
from sale.models import SaleOrder, SaleItem
from inventory.models import StockOut, StockOutItem
from decimal import Decimal


class Command(BaseCommand):
    help = '初始化销售出库单示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化销售出库单示例数据...')
        
        User = get_user_model()
        admin_user = User.objects.filter(username='admin').first()
        warehouse = Warehouse.objects.filter(name='主仓库').first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('请先运行 init_data 创建管理员用户'))
            return
        
        if not warehouse:
            self.stdout.write(self.style.ERROR('请先运行 init_data 创建仓库'))
            return
        
        goods_list = list(Goods.objects.all()[:4])
        if len(goods_list) < 2:
            self.stdout.write(self.style.ERROR('请先运行 init_data 创建商品'))
            return
        
        self.create_sample_data(admin_user, warehouse, goods_list)
        
        self.stdout.write(self.style.SUCCESS('销售出库单示例数据初始化完成！'))

    def create_sample_data(self, admin_user, warehouse, goods_list):
        """创建示例数据"""
        customer = Customer.objects.first()
        if not customer:
            self.stdout.write(self.style.WARNING('未找到客户，跳过创建销售订单关联'))
        
        for i in range(3):
            sale_order = None
            if customer:
                sale_order, _ = SaleOrder.objects.get_or_create(
                    order_no=f'SO2026031100{i+1}',
                    defaults={
                        'customer': customer,
                        'warehouse': warehouse,
                        'order_date': f'2026-03-11',
                        'total_amount': Decimal('500.00') * (i + 1),
                        'status': 'completed',
                        'created_by': admin_user
                    }
                )
                
                for j, goods in enumerate(goods_list[:2]):
                    SaleItem.objects.get_or_create(
                        order=sale_order,
                        goods=goods,
                        defaults={
                            'quantity': 10 * (j + 1),
                            'price': goods.sale_price or Decimal('50.00'),
                            'amount': (goods.sale_price or Decimal('50.00')) * 10 * (j + 1)
                        }
                    )
            
            stock_out, created = StockOut.objects.get_or_create(
                order_no=f'SO2026031100{i+1}',
                defaults={
                    'warehouse': warehouse,
                    'sale_order': sale_order,
                    'total_amount': Decimal('500.00') * (i + 1),
                    'status': 'confirmed',
                    'remark': f'示例出库单{i+1}',
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(f'  创建出库单: {stock_out.order_no}')
                
                for j, goods in enumerate(goods_list[:2]):
                    StockOutItem.objects.create(
                        stock_out=stock_out,
                        goods=goods,
                        quantity=10 * (j + 1),
                        price=goods.sale_price or Decimal('50.00'),
                        amount=(goods.sale_price or Decimal('50.00')) * 10 * (j + 1)
                    )
            else:
                self.stdout.write(f'  出库单已存在: {stock_out.order_no}')
