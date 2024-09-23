from django.urls import path,include
from .import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
urlpatterns = [
    
    path('', views.index, name='home'),  # Root URL
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),   
    path('login/',views.login_view,name='login'),
    path('farmer_dashboard/',views.farmer_dashboard,name='farmer_dashboard'),
    path('post_rambutan/',views.post_rambutan,name='post_rambutan'),
    path('view_posts/',views.view_posts,name='view_posts'),
    path('customer_dashboard/',views.customer_dashboard, name='customer_dashboard'),
    path('farmer-details/', views.farmer_details, name='farmer_details'),
    path('profile/', views.profile_view, name='profile_view'),
    path('products/', views.products_browse, name='products_browse'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('cart/', views.cart, name='cart'),
    path('logout/', views.logout_view, name='logout'),
    path('tree/',views.create_tree_variety),
    path('farmer/',views.create_farmer_details),
    path('ram/',views.create_rambutan_post),
    path('contact/',views.contact,name='contact'),
    path('profile_view/',views.profile_view,name='profile_view'),
    path('customer_details/',views.customer_details,name='customer_details'),
    path('productsingle/',views.product_single,name='product_single'),
    path('checkout/',views.checkout,name='checkout'),
    path('blog/',views.blog,name='blog')
]



