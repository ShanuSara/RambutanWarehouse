import re
from django import forms
from .models import CustomerDetails, FarmerDetails, TreeVariety,RambutanPost,Registeruser, Wishlist
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

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
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


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
        fields = [ 'name', 'variety', 'quantity', 'price_per_kg', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'quantity': forms.NumberInput(attrs={'min': 2}),
            'price_per_kg': forms.NumberInput(attrs={'min':0 , 'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False  # Make image field optional

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['rambutan_post'] 
