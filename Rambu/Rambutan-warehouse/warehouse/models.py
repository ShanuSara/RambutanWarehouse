from datetime import timezone
from django.utils import timezone
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
    is_active = models.BooleanField(default=True) 
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
    
    # Sorted product choices in ascending order, 'Other' is at the bottom
    PRODUCT_CHOICES = sorted([
        ('Binjai', 'Binjai'),
        ('Caesar', 'Caesar'),
        ('E35', 'E35'),
        ('Hg Deli Baling', 'Hg Deli Baling'),
        ('Jarum Emas', 'Jarum Emas'),
        ('Maharlika', 'Maharlika'),
        ('Malwana', 'Malwana'),
        ('Muar Gading', 'Muar Gading'),
        ('Rambutan N18', 'Rambutan N18'),
        ('Rongrien', 'Rongrien'),
        ('School Boy', 'School Boy'),
        ('other', 'Other')  # 'Other' option placed last
    ], key=lambda x: (x[0] != 'other', x[0]))  # Ensures 'Other' is last

    product = models.CharField(max_length=255, choices=PRODUCT_CHOICES)
    
    CATEGORY_CHOICES = [
        ('fresh_fruit', 'Fresh Fruit'),
        ('juice', 'Juice'),
        ('pickle', 'Pickle'),
        ('wine', 'Wine'),
        
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    quantity_type = models.CharField(max_length=10, choices=[('kg', 'Kilograms'), ('L', 'Litres')])
    quantity = models.PositiveIntegerField(default=1)
    quantity_left = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image = models.ImageField(upload_to='rambutan_images/')
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product} - {self.quantity} {self.quantity_type}"

    def save(self, *args, **kwargs):
        if isinstance(self.quantity, str):
            self.quantity = int(self.quantity)  # Convert to int if it's a string
        if self.quantity < 0:
            raise ValueError("Quantity must be a non-negative integer.")
        
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
            message='Phone number must be entered in the format, eg: +918541744560. Up to 15 digits allowed.'
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
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    billing_detail = models.ForeignKey(BillingDetail, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    
    # Payment related fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Status fields
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Delivery boy assignment
    delivery_boy = models.ForeignKey(
        'DeliveryBoy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_number} - {self.user.username} - Total: {self.total_amount}'
    
    def update_status(self, new_status, delivery_boy):
        now = timezone.now()
        if new_status == 'packed':
            self.packed_at = now
        elif new_status == 'shipped':
            self.shipped_at = now
        elif new_status == 'out_for_delivery':
            self.out_for_delivery_date = now
        elif new_status == 'delivered':
            self.delivery_date = now
        
        self.order_status = new_status
        self.save()
        
        # Create status update record
        OrderStatusUpdate.objects.create(
            order=self,
            delivery_boy=delivery_boy,
            status=new_status
        )
        
        # Create or update timestamp record
        OrderStatusTimestamp.objects.update_or_create(
            order=self,
            status=new_status,
            defaults={'timestamp': now, 'updated_by': delivery_boy}
        )

    def assign_delivery_boy(self):
        # Find available delivery boy who has the least number of active orders
        available_delivery_boy = DeliveryBoy.objects.filter(
            approval_status='approved',
            is_available=True
        ).annotate(
            active_orders=models.Count(
                'assigned_orders',
                filter=models.Q(
                    assigned_orders__order_status__in=[
                        'pending', 'processing', 'packed', 'out_for_delivery'
                    ]
                )
            )
        ).order_by('active_orders').first()

        if available_delivery_boy:
            self.delivery_boy = available_delivery_boy
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new order
        super().save(*args, **kwargs)
        
        # If this is a new order and no delivery boy is assigned, try to assign one
        if is_new and not self.delivery_boy:
            self.assign_delivery_boy()
            
            # Send notification to the assigned delivery boy if one was found
            if self.delivery_boy:
                # Import here to avoid circular import
                from django.core.mail import send_mail
                from django.conf import settings

                subject = 'New Delivery Assignment'
                message = f'''
                You have been assigned a new delivery:
                Order #{self.order_number}
                Delivery Address: {self.billing_detail.street_address}, {self.billing_detail.city}
                Customer: {self.user.name}
                Phone: {self.billing_detail.phone}
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.delivery_boy.user.username],  # Email is stored in username field
                    fail_silently=True,
                )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    #cart_item = models.ForeignKey(Cart, on_delete=models.CASCADE)  
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f'{self.order.order_number} - Quantity: {self.quantity}' 


class OrderNotification(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50)
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.order_number} - {self.item_name}'

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback')
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, null=True, blank=True)  
    content = models.TextField()  
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])     
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Feedback from {self.user} - {self.content[:20]}"  

class DeliveryBoy(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    user = models.OneToOneField(Registeruser, on_delete=models.CASCADE, related_name='delivery_boy')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[6-9]\d{9}$', 'Enter a valid Indian phone number.')],
    )
    address = models.TextField()
    license_number = models.CharField(
        max_length=16,
        validators=[RegexValidator(
            r'^(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9][0-9])[0-9]{7}$',
            'Enter a valid driving license number.'
        )],
    )
    is_available = models.BooleanField(default=True)
    approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.phone}"

    class Meta:
        verbose_name = 'Delivery Boy'
        verbose_name_plural = 'Delivery Boys' 

    def get_active_orders_count(self):
        return self.assigned_orders.filter(
            order_status__in=['pending', 'processing', 'packed', 'out_for_delivery']
        ).count()

    def is_available_for_orders(self):
        # You can add additional conditions here
        return (
            self.is_available 
            and self.approval_status == 'approved'
            and self.get_active_orders_count() < 10  # Maximum 10 active orders per delivery boy
        )

class BidPost(models.Model):
    rambutan_post = models.ForeignKey(RambutanPost, on_delete=models.CASCADE, related_name='bid_posts')
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    bid_quantity = models.PositiveIntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bid for {self.rambutan_post.product} - Current Price: {self.current_price}"

    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.start_price
        if self.start_price <= 0:
            raise ValidationError("Starting price must be greater than 0")
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date")
        
        now = timezone.now()
        if now >= self.start_date and now <= self.end_date:
            self.is_active = True
        else:
            self.is_active = False
            
        super().save(*args, **kwargs)

class CustomerBid(models.Model):
    bid_post = models.ForeignKey(BidPost, on_delete=models.CASCADE, related_name='customer_bids')
    customer = models.ForeignKey(Registeruser, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bid_amount']

    def __str__(self):
        return f"{self.customer.name} bid ₹{self.bid_amount} on {self.bid_post}" 

class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.order.order_number} - {self.status} by {self.delivery_boy.full_name}" 

class OrderStatusTimestamp(models.Model):
    """Model to store timestamps for each order status change"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_timestamps')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(DeliveryBoy, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['order', 'status']  # Only one timestamp per status per order
    
    def __str__(self):
        return f"Order #{self.order.order_number} - {self.status} at {self.timestamp}"

class Meeting(models.Model):
    bid = models.ForeignKey(BidPost, on_delete=models.CASCADE)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farmer_meetings')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_meetings')
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    duration = models.IntegerField()  # in minutes
    meeting_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    suggested_date = models.DateField(null=True, blank=True)
    suggested_time = models.TimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['meeting_date', 'meeting_time']
        
    def __str__(self):
        return f"Meeting between {self.farmer.username} and {self.customer.username} on {self.meeting_date}"
