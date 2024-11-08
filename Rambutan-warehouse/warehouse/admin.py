from django.contrib import admin
from .models import BillingDetail, Cart, CustomerDetails, Feedback, Order, OrderItem, RambutanPost, Registeruser,FarmerDetails, TreeVariety , Wishlist

class RegisteruserAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'contact', 'role', 'place','is_active')  
    search_fields = ('name', 'username', 'contact') 
    list_filter = ('role', 'place')

admin.site.register(Registeruser, RegisteruserAdmin)

@admin.register(FarmerDetails)
class FarmerDetailsAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'aadhar_number','bank_name','location')
    search_fields = ('mobile_number', 'location', 'aadhar_number','bank_name')
    list_filter = ('location',)
    
@admin.register(CustomerDetails)
class CustomerDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'location', 'total_orders', 'total_amount_spent')
    search_fields = ('mobile_number', 'location', 'user__username')
    list_filter = ('location',)  

@admin.register(TreeVariety)
class TreeVarietyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class RambutanPostAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'product', 'quantity', 'quantity_left', 'price', 'is_available', 'created_at')
    fields = ('farmer', 'product', 'quantity_type', 'quantity', 'price', 'image', 'description', 'quantity_left', 'is_available', 'created_at')
    search_fields = ['product', 'farmer__name']
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('product') == 'other':
            obj.product = form.cleaned_data.get('other_product')
        super().save_model(request, obj, form, change)

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

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'rambutan_post', 'quantity']  

admin.site.register(OrderItem, OrderItemAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rambutan_post', 'rating', 'created_at', 'updated_at')
    search_fields = ('user__username', 'rambutan_post__title', 'content')
    list_filter = ('rating', 'created_at')

admin.site.register(Feedback, FeedbackAdmin)
