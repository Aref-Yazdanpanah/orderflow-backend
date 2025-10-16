from django.contrib import admin

from .models import Order, OrderItem, Product

admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
