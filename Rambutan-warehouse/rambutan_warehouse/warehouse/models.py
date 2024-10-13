from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator,MinLengthValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.forms import ValidationError

ROLE_CHOICES = [
    ('farmer', 'Farmer'),
    ('customer', 'Customer'),
]

class Registeruser(AbstractUser):
    username = models.EmailField(unique=True)
    name = models.CharField(max_length=50,default='noname')
    contact = models.CharField(max_length=250, blank=True)
    address = models.CharField(max_length=250, blank=True) 
    place = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        Group,
        related_name='registeruser_set',  # Custom related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='registeruser_set',  # Custom related_name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username
    
class TreeVariety(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class FarmerDetails(models.Model):
    MOBILE_NUMBER_PATTERN = '^[6-9]\d{9}$'
    AADHAR_NUMBER_PATTERN = '^\d{12}$'
    ACCOUNT_NUMBER_PATTERN = '^\d{9,18}$'
    IFSC_CODE_PATTERN = '^[A-Z]{4}0[A-Z0-9]{6}$'
    user = models.OneToOneField(Registeruser, on_delete=models.CASCADE, related_name='farmerdetails')
    address = models.TextField()
    mobile_number = models.CharField(max_length=10)
    location = models.CharField(max_length=255)
    aadhar_number = models.CharField(max_length=12)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=18)
    ifsc_code = models.CharField(max_length=11)
    #tree_variety = models.ManyToManyField(TreeVariety, related_name='farmers')
    #total_trees = models.PositiveIntegerField()
    #total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.mobile_number} - {self.location}"

class CustomerDetails(models.Model):
    MOBILE_NUMBER_PATTERN = '^[6-9]\d{9}$'  

    user = models.OneToOneField(Registeruser, on_delete=models.CASCADE, related_name='customerdetails')
    address = models.TextField()  
    mobile_number = models.CharField(max_length=10)  
    location = models.CharField(max_length=255, blank=True, null=True) 
    total_orders = models.PositiveIntegerField(default=0)  
    total_amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    def __str__(self):
        return f"{self.user.username} - {self.mobile_number}"

class RambutanPost(models.Model):
    farmer = models.ForeignKey('FarmerDetails', on_delete=models.CASCADE, related_name='rambutan_posts')
    name = models.CharField(max_length=255)
    variety = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField() 
    quantity_left = models.PositiveIntegerField(default=0)  # Quantity left after sales
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rambutan_images/', blank=True, null=True) 
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)  # Whether the post is still available
    
    def __str__(self):
        return f"{self.name} ({self.variety}) - {self.quantity}kg"
    def save(self, *args, **kwargs):

        # Update availability status based on quantity left
        #if self.quantity_left <=0:
          #  self.is_available = False
        #else:
          #  self.is_available = True
        super().save(*args, **kwargs)

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, related_name='wishlists')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'rambutan_post')

class FarmerProfile(models.Model):
    farmer = models.OneToOneField(FarmerDetails, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.farmer}"
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, related_name='carts')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'rambutan_post')  

    def save(self, *args, **kwargs):
        if self.price is not None and self.quantity is not None:
            self.total_price = self.price * self.quantity
        else:
            self.total_price = 0  
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.rambutan_post} - Quantity: {self.quantity}'

class BillingDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_details')
    
    first_name = models.CharField(max_length=100, validators=[MinLengthValidator(2)], blank=False)
    last_name = models.CharField(max_length=100, validators=[MinLengthValidator(2)], blank=False)
    
    country = models.CharField(max_length=100, blank=False)
    street_address = models.CharField(max_length=255, blank=False)
    city = models.CharField(max_length=100, blank=False)
    
    postcode = models.CharField(max_length=20, blank=False, validators=[
        RegexValidator(
            regex=r'^\d{4,10}$',
            message='Postcode must be a number between 4 and 10 digits.'
        )
    ])
    
    phone = models.CharField(max_length=20, blank=False, validators=[
        RegexValidator(
            regex=r'^\+?\d{9,15}$',
            message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.'
        )
    ])
    
    email = models.EmailField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'

    def clean(self):
      
        if not self.email:
            raise ValidationError('Email is required.')
        if not self.phone.isdigit():
            raise ValidationError('Phone number must contain only digits.')

class Order(models.Model):
    billing_detail = models.ForeignKey(BillingDetail, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    order_number = models.AutoField(primary_key=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  

    def __str__(self):
        return f'Order {self.order_number} - {self.user.username} - Total: {self.total_amount}'
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    #cart_item = models.ForeignKey(Cart, on_delete=models.CASCADE)  
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f'{self.order.order_number} - Quantity: {self.quantity}' 

from django.db import models
from django.contrib.auth.models import User

class OrderNotification(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50)
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.order_number} - {self.item_name}'
