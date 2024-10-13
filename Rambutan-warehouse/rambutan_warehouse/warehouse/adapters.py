from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class MyAccountAdapter(DefaultAccountAdapter):
    def generate_unique_username(self, email):
        # Ensure email is a string
        if isinstance(email, list):
            email = email[0]  # Take the first email if it's a list

        # Split the email to generate the username
        username = email

        # Ensure the username is unique
        User = get_user_model()  # Use get_user_model to retrieve the user model
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{username}{i}"
            i += 1
        return username

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email:
            sociallogin.username = MyAccountAdapter().generate_unique_username(email)
