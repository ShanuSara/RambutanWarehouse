from django.urls import path,include
from .import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import  add_to_wishlist, checkout, order_detail, remove_from_wishlist
from .views import order_history

urlpatterns = [
    path('admin/', admin.site.urls),
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
    #path('cart/', views.cart, name='cart'),
    path('logout/', views.logout_view, name='logout'),
    path('tree/',views.create_tree_variety),
    path('contact/',views.contact,name='contact'),
    path('profile_view/',views.profile_view,name='profile_view'),
    path('productsingle/',views.product_single,name='product_single'),
    path('checkout/',views.checkout,name='checkout'),
    path('blog/',views.blog,name='blog'),
    path('wishlist/add/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:id>/',remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'), 
    path('view_posts/update_post/<int:id>', views.update_post, name='update_post'),
    path('post/<int:id>/delete/confirm/', views.delete_post_confirmation, name='delete_post_confirmation'),
    path('post/<int:id>/delete/', views.delete_post, name='delete_post'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:rambutan_post_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('place_order',views.place_order,name='place_order'),
    #path('order',views.order,name='order'),
    path('billing/', views.billing_view, name='billing_view'),
    path('checkout/', checkout, name='checkout'),
    path('order/<int:order_number>/', views.order_detail, name='order_detail'),
    path('order_history/', order_history, name='order_history'),

    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]



