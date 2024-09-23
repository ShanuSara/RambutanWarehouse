from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django.contrib.auth.models import AbstractUser, Group, Permission

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
    tree_variety = models.ManyToManyField(TreeVariety, related_name='farmers')
    total_trees = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rambutan_images/', blank=True, null=True) 
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.variety}) - {self.quantity}kg"
