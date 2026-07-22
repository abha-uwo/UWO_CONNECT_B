from ..models import Order
class OrderRepository:
    @staticmethod
    def filter_orders(**kwargs): return Order.objects.filter(**kwargs)
    @staticmethod
    def get_all(): return Order.objects.all()
