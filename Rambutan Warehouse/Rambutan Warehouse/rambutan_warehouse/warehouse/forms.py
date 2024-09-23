import re
from django import forms
from .models import CustomerDetails, FarmerDetails, TreeVariety,RambutanPost,Registeruser


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Registeruser
        fields = ['name', 'contact', 'address', 'place', 'username', 'password', 'role']

class FarmerDetailsForm(forms.ModelForm):
    class Meta:
        model = FarmerDetails
        fields = ['user', 'address', 'mobile_number', 'location', 'aadhar_number', 
                  'bank_name', 'account_number', 'ifsc_code', 'tree_variety', 
                  'total_trees', 'total_amount']

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
        fields = ['farmer', 'name', 'variety', 'quantity', 'price_per_kg', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'price_per_kg': forms.NumberInput(attrs={'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False  # Make image field optional

