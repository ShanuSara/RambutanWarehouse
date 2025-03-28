"""
Django settings for rambutan_warehouse project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# private_key_id = os.environ.get('private_key_id')
# private_key = os.environ.get('private_key')
# client_email = os.environ.get('client_email')
# client_id = os.environ.get('client_id')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8t!q+oas1u2!)4&1$v$522dub!*gyn-*ejtlz)2!+q1t@g%-cd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['rambutanwarehouse.onrender.com', 'localhost', '127.0.0.1:8000']
ALLOWED_HOSTS = ['*']
BASE_URLS = 'https://rambutanwarehouse.onrender.com'
PORT = os.environ.get('PORT', '8000')
print(f"Running on PORT: {PORT}")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'warehouse',
    'social_django',  
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'  
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',  
    'social_core.pipeline.social_auth.social_uid',      
    'social_core.pipeline.social_auth.auth_allowed',    
    'social_core.pipeline.social_auth.social_user',     
    'social_core.pipeline.user.get_username',          
    'social_core.pipeline.user.create_user',          
    'social_core.pipeline.social_auth.associate_user',  
    'social_core.pipeline.social_auth.load_extra_data', 
    'social_core.pipeline.user.user_details',          
)


ROOT_URLCONF = 'rambutan_warehouse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  
                'social_django.context_processors.login_redirect',  
            ],
        },
    },
]

WSGI_APPLICATION = 'rambutan_warehouse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS':{
            'min_length':8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
   
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'


# Timezone settings
TIME_ZONE = 'Asia/Kolkata'  # This is already correct for Indian time
USE_TZ = True  # This ensures Django uses timezone-aware datetimes


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "warehouse/static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

AUTH_USER_MODEL = 'warehouse.Registeruser'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your email provider's SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'rambutanwarehouse@gmail.com'
EMAIL_HOST_PASSWORD = 'irog svku pabm ndmx'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# SITE_ID = 2

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',  
]
OAUTH_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
OAUTH_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_SECRET_KEY= os.environ.get('RAZORPAY_SECRET_KEY')

# Add these settings for social-auth-app-django
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = OAUTH_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = OAUTH_SECRET

LOGIN_REDIRECT_URL = 'register'
LOGOUT_REDIRECT_URL = '/'


RAZORPAY_KEY_ID = RAZORPAY_KEY_ID
RAZORPAY_SECRET_KEY = RAZORPAY_SECRET_KEY


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\shanu\Downloads\rambutanbot-owlq-b5dc53cc5d4d.json"
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'rambutan-vision-key.json')

