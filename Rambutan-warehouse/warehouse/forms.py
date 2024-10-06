import re
from django import forms
from .models import  BillingDetail, Cart, CustomerDetails, FarmerDetails, Order, OrderItem, TreeVariety,RambutanPost,Registeruser, Wishlist
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Registeruser
        fields = ['name', 'contact', 'address', 'place', 'username', 'password', 'role']

    CONTACT_PATTERN = '^[6-9]\d{9}$'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)
        
        return password

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not re.match(self.CONTACT_PATTERN, str(contact)):
            raise ValidationError("Contact number must be a valid 10-digit number starting with 6, 7, 8, or 9.")
        
        return contact

    def clean_username(self):

        username = self.cleaned_data.get('username')
        if not self.is_valid_email(username):
            raise ValidationError("Username must be a valid email address.")
        
        return username

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]{5,}@gmail\.com$'
        return re.match(email_regex, email)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.email = self.clean_username()
        if commit:
            user.save()
        return user

'''
class FarmerDetailsForm(forms.ModelForm):
    class Meta:
        model = FarmerDetails
        fields = ['user', 'address', 'mobile_number', 'location', 'aadhar_number', 
                  'bank_name', 'account_number', 'ifsc_code','tree_variety','total_trees','total_amount']

        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'mobile_number': forms.TextInput(),
            'aadhar_number': forms.TextInput(),
            'account_number': forms.TextInput(),
            'ifsc_code': forms.TextInput(),
        }'''

class FarmerDetailsForm(forms.ModelForm):
    mobile_number = forms.CharField(
        label='Mobile Number',
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'})
    )
    
    aadhar_number = forms.CharField(
        label='Aadhaar Number',
        max_length=12,
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message="Enter a valid 12-digit Aadhaar number."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Aadhaar Number'})
    )

    account_number = forms.CharField(
        label='Account Number',
        validators=[
            RegexValidator(
                regex=r'^\d{9,18}$',
                message="Enter a valid account number (9 to 18 digits)."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Account Number'})
    )

    ifsc_code = forms.CharField(
        label='IFSC Code',
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
                message="Enter a valid IFSC code (e.g., ABCD0123456)."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'IFSC Code'})
    )

    class Meta:
        model = FarmerDetails
        fields = [
            'user', 'address', 'mobile_number', 'location', 'aadhar_number', 
            'bank_name', 'account_number', 'ifsc_code', 'tree_variety', 'total_trees', 'total_amount'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'mobile_number': forms.TextInput(),
            'aadhar_number': forms.TextInput(),
            'account_number': forms.TextInput(),
            'ifsc_code': forms.TextInput(),
        }

class CustomerDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomerDetails
        fields = ['user', 'address', 'mobile_number', 'location']  

        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your address'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location (optional)'}),
        }

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not re.match(CustomerDetails.MOBILE_NUMBER_PATTERN, mobile_number):
            raise forms.ValidationError("Enter a valid mobile number.")
        return mobile_number
    
class TreeVarietyForm(forms.ModelForm):
    class Meta:
        model = TreeVariety
        fields = ['name']

class RambutanPostForm(forms.ModelForm):
    class Meta:
        model = RambutanPost
        fields = ['name', 'variety', 'quantity', 'price_per_kg', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'value': 1}),  
            'price_per_kg': forms.NumberInput(attrs={'min': 1, 'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False  

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        price_per_kg = cleaned_data.get('price_per_kg')

        if quantity is not None and quantity < 1:
            self.add_error('quantity', 'Quantity must be at least 1.')

        if price_per_kg is not None and price_per_kg <= 0:
            self.add_error('price_per_kg', 'Price per kg must be greater than 0.')

        return cleaned_data

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['rambutan_post'] 

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['user', 'rambutan_post', 'quantity', 'price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '1'}),  
        }

class CartUpdateForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity'] 
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '1'}), 
        }


class BillingDetailForm(forms.ModelForm):
    class Meta:
        model = BillingDetail
        fields = [
            'first_name', 'last_name', 'country', 
            'street_address', 'city', 'postcode', 
            'phone', 'email'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'street_address': forms.TextInput(attrs={'placeholder': 'House number and street name'}),
            'city': forms.TextInput(attrs={'placeholder': 'Town / City'}),
            'postcode': forms.TextInput(attrs={'placeholder': 'Postcode / ZIP'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['billing_detail', 'user', 'total_amount', 'payment_method']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['order', 'quantity', 'price']
