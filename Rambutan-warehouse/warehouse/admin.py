from django.contrib import admin
from .models import CustomerDetails, Registeruser,FarmerDetails, TreeVariety , Wishlist

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
    list_display = ('name', 'variety', 'quantity', 'price_per_kg', 'farmer', 'created_at', 'image_display')
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