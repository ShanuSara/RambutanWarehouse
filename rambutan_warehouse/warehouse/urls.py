from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),  # Root URL
    path('index/', views.index_view, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('fruit/', views.fruit_view, name='fruit'),
    path('service/', views.service_view, name='service'),
]
