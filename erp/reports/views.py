from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from purchase.models import PurchaseOrder
from sale.models import SaleOrder
from inventory.models import Inventory
from finance.models import Payment
from system.permissions import ModulePermission


class ReportsModulePermission(ModulePermission):
    MODULE_MAP = {
        '采购报表': 'reports',
        '销售报表': 'reports',
        '库存报表': 'reports',
        '财务报表': 'reports',
        '仪表盘': 'reports',
    }


class PurchaseReportView(APIView):
    """采购报表"""
    permission_classes = [IsAuthenticated, ReportsModulePermission]
    module_name = '采购报表'

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = PurchaseOrder.objects.filter(status='completed')
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        order_count = queryset.count()
        
        orders = []
        for order in queryset[:50]:
            orders.append({
                'id': order.id,
                'order_no': order.order_no,
                'supplier_name': order.supplier.name if order.supplier else '',
                'order_date': order.order_date,
                'total_amount': float(order.total_amount),
                'status': order.status
            })
        
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'summary': {
                    'total_amount': float(total_amount),
                    'order_count': order_count
                },
                'orders': orders
            }
        })


class SaleReportView(APIView):
    """销售报表"""
    permission_classes = [IsAuthenticated, ReportsModulePermission]
    module_name = '销售报表'

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = SaleOrder.objects.filter(status='completed')
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        order_count = queryset.count()
        
        orders = []
        for order in queryset[:50]:
            orders.append({
                'id': order.id,
                'order_no': order.order_no,
                'customer_name': order.customer.name if order.customer else '',
                'order_date': order.order_date,
                'total_amount': float(order.total_amount),
                'status': order.status
            })
        
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'summary': {
                    'total_amount': float(total_amount),
                    'order_count': order_count
                },
                'orders': orders
            }
        })


class InventoryReportView(APIView):
    """库存报表"""
    permission_classes = [IsAuthenticated, ReportsModulePermission]
    module_name = '库存报表'

    def get(self, request):
        from basic.models import Goods, Unit, Category
        
        goods_name = request.query_params.get('goods_name', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        queryset = Inventory.objects.select_related('goods', 'warehouse').all()
        
        if goods_name:
            queryset = queryset.filter(goods__name__icontains=goods_name)
        
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        items = []
        for inv in queryset[start:end]:
            goods = inv.goods
            avg_price = goods.purchase_price if goods.purchase_price else 0
            total_value = inv.quantity * avg_price
            
            items.append({
                'id': inv.id,
                'goods_name': goods.name,
                'goods_code': goods.code,
                'specification': goods.spec or '',
                'unit_name': goods.unit.name if goods.unit else '',
                'category_name': goods.category.name if goods.category else '',
                'quantity': float(inv.quantity),
                'avg_price': float(avg_price),
                'total_value': float(total_value),
                'min_stock': float(goods.min_stock) if goods.min_stock else 0
            })
        
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'count': total,
                'results': items
            }
        })


class DashboardView(APIView):
    """仪表盘数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        
        today_purchase = PurchaseOrder.objects.filter(
            order_date=today,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        today_sale = SaleOrder.objects.filter(
            order_date=today,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        purchase_count = PurchaseOrder.objects.count()
        sale_count = SaleOrder.objects.count()
        
        from basic.models import Goods
        goods_count = Goods.objects.filter(status=1).count()
        
        from datetime import timedelta
        last_7_days = []
        last_7_days_sales = []
        last_7_days_purchases = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            last_7_days.append(date.strftime('%m-%d'))
            
            sale_amount = SaleOrder.objects.filter(
                order_date=date,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            last_7_days_sales.append(float(sale_amount))
            
            purchase_amount = PurchaseOrder.objects.filter(
                order_date=date,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            last_7_days_purchases.append(float(purchase_amount))
        
        category_value = {}
        total_inventory_value = 0
        for inv in Inventory.objects.select_related('goods').all():
            goods = inv.goods
            category = goods.category.name if goods.category else '未分类'
            value = inv.quantity * (goods.purchase_price or 0)
            category_value[category] = category_value.get(category, 0) + value
            total_inventory_value += value
        
        category_names = list(category_value.keys())
        category_values = [float(v) for v in category_value.values()]
        
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'today_purchase': float(today_purchase),
                'today_sale': float(today_sale),
                'purchase_count': purchase_count,
                'sale_count': sale_count,
                'goods_count': goods_count,
                'total_inventory_value': float(total_inventory_value),
                'chart_7_days': {
                    'dates': last_7_days,
                    'sales': last_7_days_sales,
                    'purchases': last_7_days_purchases
                },
                'chart_category': {
                    'categories': category_names,
                    'values': category_values
                }
            }
        })


class FinanceReportView(APIView):
    """财务报表"""
    permission_classes = [IsAuthenticated, ReportsModulePermission]
    module_name = '财务报表'

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payment_type = request.query_params.get('payment_type')
        
        queryset = Payment.objects.all()
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        if payment_type:
            queryset = queryset.filter(type=payment_type)
        
        total_payment = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        income = queryset.filter(type='receive').aggregate(total=Sum('amount'))['total'] or 0
        expense = queryset.filter(type='pay').aggregate(total=Sum('amount'))['total'] or 0
        
        payments = []
        for payment in queryset[:50]:
            related_party_name = ''
            if payment.related_party_type == 'supplier':
                from basic.models import Supplier
                try:
                    supplier = Supplier.objects.get(id=payment.related_party_id)
                    related_party_name = supplier.name
                except:
                    pass
            elif payment.related_party_type == 'customer':
                from basic.models import Customer
                try:
                    customer = Customer.objects.get(id=payment.related_party_id)
                    related_party_name = customer.name
                except:
                    pass
            
            payments.append({
                'id': payment.id,
                'payment_no': payment.order_no,
                'payment_type': payment.get_type_display(),
                'related_party_name': related_party_name,
                'amount': float(payment.amount),
                'payment_date': payment.created_at.strftime('%Y-%m-%d') if payment.created_at else '',
                'payment_method': payment.payment_method or '',
                'remark': payment.remark or ''
            })
        
        return Response({
            'code': 200,
            'msg': '成功',
            'data': {
                'summary': {
                    'total_payment': float(total_payment),
                    'income': float(income),
                    'expense': float(expense),
                    'net_profit': float(income - expense),
                    'payment_count': len(payments)
                },
                'payments': payments
            }
        })
