from django.contrib import admin
from .models import BillingDetail, Cart, CustomerDetails, Order, OrderItem, Registeruser,FarmerDetails, TreeVariety , Wishlist

class RegisteruserAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'contact', 'role', 'place')  
    search_fields = ('name', 'username', 'contact') 
    list_filter = ('role', 'place')

admin.site.register(Registeruser, RegisteruserAdmin)

@admin.register(FarmerDetails)
class FarmerDetailsAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'aadhar_number','bank_name','location', 'total_trees', 'total_amount')
    search_fields = ('mobile_number', 'location', 'aadhar_number','bank_name')
    list_filter = ('tree_variety','location',)
    
@admin.register(CustomerDetails)
class CustomerDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'location', 'total_orders', 'total_amount_spent')
    search_fields = ('mobile_number', 'location', 'user__username')
    list_filter = ('location',)  

@admin.register(TreeVariety)
class TreeVarietyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

from django.contrib import admin
from .models import RambutanPost

class RambutanPostAdmin(admin.ModelAdmin):
    list_display = ('name', 'variety', 'quantity', 'price_per_kg', 'farmer', 'created_at', 'image_display','is_available','quantity_left')
    list_filter = ('variety', 'created_at', 'farmer')
    search_fields = ('name', 'variety', 'farmer__name')  
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fields = ('farmer', 'name', 'variety', 'quantity', 'price_per_kg', 'image', 'description', 'created_at')

    def image_display(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 50px; height: 50px;" />'
        return 'No Image'
    image_display.allow_tags = True
    image_display.short_description = 'Image'

admin.site.register(RambutanPost, RambutanPostAdmin)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'rambutan_post', 'added_at')  
    search_fields = ('user__username', 'rambutan_post__name')  
    list_filter = ('user',)  

admin.site.register(Wishlist, WishlistAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'rambutan_post', 'quantity', 'price', 'total_price', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'rambutan_post__title') 
    readonly_fields = ('total_price', 'added_at') 
    autocomplete_fields = ['user', 'rambutan_post'] 

    def save_model(self, request, obj, form, change):
        if not obj.price:
            obj.price = 0  
        obj.total_price = obj.price * obj.quantity
        super().save_model(request, obj, form, change)

admin.site.register(Cart, CartAdmin)


class BillingDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')

admin.site.register(BillingDetail, BillingDetailAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'created_at')
    search_fields = ('user__username', 'order_number')
    inlines = [OrderItemInline]  

admin.site.register(Order, OrderAdmin)
'''
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'quantity', 'price')
    search_fields = ('order__order_number', )

admin.site.register(OrderItem, OrderItemAdmin)'''
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'rambutan_post', 'quantity']  # Add fields that actually exist in the model

admin.site.register(OrderItem, OrderItemAdmin)
