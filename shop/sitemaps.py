from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from shop.models import Product, Category

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True).order_by('order', 'name')

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return [
            ('shop:home', 1.0, 'daily'),
            ('shop:catalog', 0.9, 'daily'),
            ('shop:shipping_warranty', 0.6, 'monthly'),
            ('shop:contact', 0.6, 'monthly'),
            ('shop:legal', 0.4, 'monthly'),
            ('shop:terms', 0.4, 'monthly'),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]
