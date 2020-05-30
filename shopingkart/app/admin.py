from django.contrib import admin
from .models import CustomerRegistration, Address, Item, OrderItem, Coupon, Order, Payment, UserProfile, ShopkeeperContact



admin.site.register(CustomerRegistration)
admin.site.register(Address)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(UserProfile)
admin.site.register(ShopkeeperContact)