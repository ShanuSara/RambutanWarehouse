from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

ROLE_CHOICES = [
    ('farmer', 'Farmer'),
    ('customer', 'Customer'),
]

class Registeruser(AbstractUser):
    contact = models.CharField(max_length=250,blank=True)
    address = models.CharField(max_length=250,blank=True) 
    place = models.CharField(max_length=100,blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username