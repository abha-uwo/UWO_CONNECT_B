from ..models import Product
class ProductRepository:
    @staticmethod
    def filter_products(**kwargs): return Product.objects.filter(**kwargs)
    @staticmethod
    def get_all(): return Product.objects.all()
