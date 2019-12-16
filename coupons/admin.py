from django.contrib import admin
from .models import Coupon


# 1st variant
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']

# 2nd variant
# class CouponAdmin(admin.ModelAdmin):
#     list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
#     list_filter = ['active', 'valid_from', 'valid_to']
#     search_fields = ['code']
# admin.site.register(Coupon, CouponAdmin)

