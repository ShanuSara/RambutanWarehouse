from datetime import timedelta
from django.utils import timezone
import random
from urllib import request
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from .forms import FarmerDetailsForm,FarmerDetails, FeedbackForm,RambutanPostForm,RegisterUserForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  BillingDetail, Cart, CustomerDetails, FarmerDetails, Feedback, Order, OrderItem, OrderNotification, RambutanPost,Registeruser, Wishlist
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .forms import FarmerDetailsForm, TreeVarietyForm, RambutanPostForm
from django.contrib import messages
from django.db.models import F,Q
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model

def index(request):
    if request.method =='POST':
        pass
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

otp_storage = {}

def send_otp_email(user_email):
    otp = random.randint(1000, 9999) 
    otp_storage[user_email] = otp 

    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Please use this to verify your email.'
    from_email = 'rambutanwarehouse@gmail.com' 
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

def enter_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Registeruser.objects.filter(username=email).exists():
            messages.info(request, "Email is already registered. Please log in.")
            return redirect('login')

        send_otp_email(email)

        request.session['user_email'] = email

        return redirect('verify_otp')

    return render(request, 'enter_email.html')

def verify_otp(request):
    email = request.session.get('user_email') 

    if not email:
        # messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        if otp_storage.get(email) and otp_storage[email] == int(otp_input):
          
            del otp_storage[email]
            request.session['verified_email'] = email

            return redirect('register')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')

def register(request):
    email = request.session.get('verified_email') 

    # Check if user is signing in with Google
    if request.user.is_authenticated and request.user.email:
        email = request.user.email  # Use the email provided by Google
        if email:
            request.session['verified_email'] = email  

    # If there's no verified email (either from session or Google), redirect to email entry page
    if not email:
        messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            if email != form.cleaned_data['username']:
                messages.error(request, "Please register with the email you verified.")
                return redirect('register')

            user = form.save(commit=False)
            user.username = email 
            user.is_active = True 
            user.save()

            del request.session['verified_email']

            subject = "Welcome to Our Website"
            message = f"Dear {user.username},\n\nThank you for registering at our website."
            recipient_list = [user.username] 
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, recipient_list)

            # Log the user in automatically if Google sign-in
            if request.user.is_authenticated:
                login(request, user)

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        
        form = RegisterUserForm(initial={'username': email})

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        print(username, password)
        
        user = authenticate(request, username=username, password=password)
        print(user)
        
        if user is not None:
            login(request, user)
            
            request.session['user_id'] = user.id
            request.session['name'] = user.username
            request.session['role'] = user.role
            
            if user.is_superuser:  
                return redirect('admin_dashboard')  #  admin dashboard 
            elif user.role == 'farmer':
                return redirect('farmer_dashboard')  # Redirect to farmer dashboard
            elif user.role == 'customer':
                return redirect('customer_dashboard')  # Redirect to customer dashboard
            else:
                
                return render(request, 'login.html', {'error': 'Invalid user role'})
        else:
            messages.error(request, message="Invalid Credentials")
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_dashboard(request):
    try:
        user = Registeruser.objects.get(username=request.user.username,role='farmer')
    except Registeruser.DoesNotExist:
        return render(request, '404.html')  
    return render(request, 'farmer_dashboard.html', {'farmer': user})


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_farmer_profile(request):
    user_instance = get_object_or_404(Registeruser, username=request.user.username)

    try:
        farmer_details_instance = FarmerDetails.objects.get(user=user_instance)
    except FarmerDetails.DoesNotExist:
        return redirect(reverse('farmer_details'))  

    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        place = request.POST.get('place')
        mobile_number = request.POST.get('mobile_number')
        location = request.POST.get('location')
        aadhar_number = request.POST.get('aadhar_number')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        
        user_instance.name = name
        user_instance.contact = contact
        user_instance.address = address
        user_instance.place = place
        user_instance.save()
        
        farmer_details_instance.mobile_number = mobile_number
        farmer_details_instance.location = location
        farmer_details_instance.aadhar_number = aadhar_number
        farmer_details_instance.bank_name = bank_name
        farmer_details_instance.account_number = account_number
        farmer_details_instance.ifsc_code = ifsc_code
        farmer_details_instance.save()

        return redirect(reverse('farmer_dashboard'))
    
    return render(request, 'edit_farmer_profile.html', {
        'user_instance': user_instance,
        'farmer_details_instance': farmer_details_instance
    })

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_details(request):
    try:
        farmer_details = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        farmer_details = None

    if request.method == 'POST':
        address = request.POST.get('address')
        mobile_number = request.POST.get('mobile_number')
        aadhar_number = request.POST.get('aadhar_number')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        bank_name = request.POST.get('bank_name')
        location = request.POST.get('location')
        
        if farmer_details:
            farmer_details.address = address
            farmer_details.mobile_number = mobile_number
            farmer_details.aadhar_number = aadhar_number
            farmer_details.account_number = account_number
            farmer_details.ifsc_code = ifsc_code
            farmer_details.bank_name = bank_name
            farmer_details.location = location
        
            farmer_details.save()
        else:
            farmer_details = FarmerDetails.objects.create(
                user=request.user,
                address=address,
                mobile_number=mobile_number,
                aadhar_number=aadhar_number,
                account_number=account_number,
                ifsc_code=ifsc_code,
                bank_name=bank_name,
                location=location,
               
            )

        return redirect('farmer_dashboard')
    return render(request, 'farmer_details.html', {
        'farmer_details': farmer_details
    })


PRODUCT_CHOICES = [
    ('Muar Gading', 'Muar Gading'),
    ('Caesar', 'Caesar'),
    ('Hg Deli Baling', 'Hg Deli Baling'),
    ('Jarum Emas', 'Jarum Emas'),
    ('E35', 'E35'),
    ('Binjai', 'Binjai'),
    ('Malwana', 'Malwana'),
    ('School Boy', 'School Boy'),
    ('Maharlika', 'Maharlika'),
    ('Rongrien', 'Rongrien'),
    ('Rambutan N18', 'Rambutan N18'),
    ('other', 'Other'),
]
CATEGORY_CHOICES = [
        ('fresh_fruit', 'Fresh Fruit'),
        ('juice', 'Juice'),
        ('pickle', 'Pickle'),
        ('wine', 'Wine'),
        
    ]

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def post_rambutan(request):
    try:
        farmer = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        return redirect(reverse('farmer_details'))

    if request.method == "POST":
        product = request.POST.get('product')
        category = request.POST.get('category') 
        quantity_type = request.POST.get('quantity_type')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        description = request.POST.get('description')
        other_product_name = request.POST.get('other_product') if product == 'other' else None
        image = request.FILES.get('image')

        if product == 'other' and not other_product_name:
            return redirect(reverse('post_rambutan')) 
        rambutan_post = RambutanPost(
            farmer=farmer,
            product=other_product_name if product == 'other' else product,
            category=category,
            quantity_type=quantity_type,
            quantity=quantity,
            quantity_left=quantity,
            price=price,
            description=description,
            image=image
        )
        rambutan_post.save()
        
        request.user.is_active = True
        request.user.save()

        return HttpResponseRedirect(reverse('view_posts'))

    context = {'PRODUCT_CHOICES': PRODUCT_CHOICES}
    return render(request, 'post_rambutan.html', context)

def create_tree_variety(request):
    if request.method == 'POST':
        form = TreeVarietyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')
        else:
            messages.error(request,message=form.errors)    
    else:
        form = TreeVarietyForm()
    return render(request, 'forms.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_posts(request):
    user = request.user

    try:
        farmer_details = user.farmerdetails

        available_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=True)
        out_of_stock_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=False, quantity_left=0)
        unavailable_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=False).exclude(quantity_left=0)

    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details')

    context = {
        'available_posts': available_posts,
        'out_of_stock_posts': out_of_stock_posts,
        'unavailable_posts': unavailable_posts,
        'user': user,
    }

    return render(request, 'view_posts.html', context)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_post(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    farmer_details = get_object_or_404(FarmerDetails, user=request.user)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.farmer = farmer_details

            updated_post.quantity_left = updated_post.quantity

            if form.cleaned_data.get('product') == 'other':
                updated_post.product = request.POST.get('other_product')
            else:
                updated_post.product = form.cleaned_data.get('product')

            updated_post.category = form.cleaned_data.get('category')
            updated_post.is_available = True
            updated_post.save()
            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})
    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_quantity(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity_left')

        if new_quantity is not None:
            
                new_quantity = int(new_quantity)
                post.quantity_left = new_quantity
                post.quantity=new_quantity

                if new_quantity > 0:
                    post.is_available = True
                else:
                    post.is_available = False

                post.save()
                return redirect('view_posts')

    return render(request, 'update_quantity.html', {'post': post})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_post_confirmation(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    in_cart = Cart.objects.filter(rambutan_post=post).exists()
    in_wishlist = Wishlist.objects.filter(rambutan_post=post).exists()
    in_order = OrderItem.objects.filter(rambutan_post=post).exists()

    if request.method == 'POST':
        if in_order:
            return redirect('view_posts')

        if in_cart or in_wishlist:
            post.is_available = False 
            post.save()
        else:
            post.delete() 
        
        return redirect('view_posts')

    return render(request, 'delete_post_confirmation.html', {
        'post': post,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'in_order': in_order,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_post(request, id):
    return redirect('delete_post_confirmation', id=id)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_orders(request):
    try:
        farmer_details = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        return redirect(reverse('farmer_details'))
    
    farmer_posts = RambutanPost.objects.filter(farmer=farmer_details)
    
    order_items = OrderItem.objects.filter(
        rambutan_post__in=farmer_posts
    ).select_related('order', 'rambutan_post').order_by('-order__created_at')
    
    orders_by_number = {}
    for item in order_items:
        order_number = item.order.order_number
        if order_number not in orders_by_number:
            orders_by_number[order_number] = []
        orders_by_number[order_number].append(item)

    context = {
        'orders_by_number': orders_by_number,
    }

    return render(request, 'order_farmer.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html', {'cart': cart})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request):
    return render(request, 'edit_profile.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_single(request):
    return render(request, 'product-single.html')


@login_required
def blog(request):
    return render(request, 'blog.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile_view(request):
   
    return render(request, 'customer_profile.html')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_customer_profile(request):
    user = get_object_or_404(Registeruser, username=request.user.username)  
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.address = request.POST.get('address')
        user.contact = request.POST.get('contact')
        user.place = request.POST.get('place')
        user.save() 
        return redirect('profile_view') 
    return render(request, 'edit_customer_profile.html', {'user': user})  

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def products_browse(request):
    category_filter = request.GET.get('category', '')  
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products_query = RambutanPost.objects.all()
    if category_filter:
        products_query = products_query.filter(category=category_filter)
    if min_price:
        products_query = products_query.filter(price__gte=min_price)
    if max_price:
        products_query = products_query.filter(price__lte=max_price)

    products = products_query.values(
        'id', 'product', 'category', 'image', 'price', 'created_at', 'description',
        'is_available', 'quantity_left', 'farmer','quantity_type'
    )

    cart_items = Cart.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)

    for product in products:
        if product['quantity_left'] <= 0:
            product['status_message'] = 'Out of Stock'
        elif not product['is_available']:
            product['status_message'] = 'Unavailable'

    context = {
        'products': products,
        'category_filter': category_filter,  
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_detail(request, product_id):
    product = get_object_or_404(RambutanPost, id=product_id)
    
    feedbacks = Feedback.objects.filter(rambutan_post=product).order_by('-created_at')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.rambutan_post = product  
            feedback.user = request.user  
            feedback.save()
            return redirect('product_detail', product_id=product.id) 
    else:
        form = FeedbackForm()

    context = {
        'product': product,
        'feedbacks': feedbacks,
        'form': form,
    }
    
    return render(request, 'product_details.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('rambutan_post')

    wishlists = RambutanPost.objects.filter(id__in=[item.rambutan_post_id for item in wishlist_items])

    return render(request, 'wishlist.html', {'wishlist_items': wishlists})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        rambutan_post=post
    )

    if not post.is_available and created:
        messages.warning(request, f"{post.name} is currently unavailable, but it has been added to your wishlist.")

    return redirect('wishlist')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def remove_from_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    wishlist_item = Wishlist.objects.filter(user=request.user, rambutan_post=post).first()

    if wishlist_item:
        wishlist_item.delete()

    return redirect('wishlist')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request, rambutan_post_id):
    rambutan_post = get_object_or_404(RambutanPost, id=rambutan_post_id)

    if not rambutan_post.is_available:
        messages.warning(request, f"{rambutan_post.name} is currently unavailable. You can keep it in your cart but cannot purchase it.")
    else:
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, 
            rambutan_post=rambutan_post,
            defaults={'price': rambutan_post.price} 
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
    
    return redirect('cart')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.price * item.quantity
    total_price = sum(item.total_price for item in cart_items) 
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    
    return render(request, 'cart.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    
    return redirect('cart') 


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        
        rambutan_post = get_object_or_404(RambutanPost, id=cart_item.rambutan_post_id)

        if new_quantity <= rambutan_post.quantity_left:
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
        else:
            messages.error(request, f"Cannot add more than available quantity. Available: {rambutan_post.quantity_left}.")
            return redirect('cart')

    return redirect('cart')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def billing_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
        rambutan_post = cart_item.rambutan_post
        
        if cart_item.quantity > rambutan_post.quantity_left:
            messages.error(request, f"Sorry, the quantity of '{rambutan_post.name}' in your cart exceeds the available stock.")
            return redirect('cart') 
    billing_details = BillingDetail.objects.filter(user=request.user).last()

    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        country = request.POST.get('country')
        street_address = request.POST.get('street-address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        if not all([first_name, last_name, country, street_address, city, postcode, phone, email]):
            messages.error(request, "All fields are required. Please fill in all details.")
            return redirect('place_order')

        if billing_details:
            billing_details.first_name = first_name
            billing_details.last_name = last_name
            billing_details.country = country
            billing_details.street_address = street_address
            billing_details.city = city
            billing_details.postcode = postcode
            billing_details.phone = phone
            billing_details.email = email
            billing_details.save()
        else:
            BillingDetail.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                country=country,
                street_address=street_address,
                city=city,
                postcode=postcode,
                phone=phone,
                email=email
            )

        return redirect('place_order')

    return render(request, 'checkout.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_billing_details(request, pk):
    billing_details = get_object_or_404(BillingDetail, pk=pk)

    if request.method == 'POST':
        billing_details.first_name = request.POST.get('first-name')
        billing_details.last_name = request.POST.get('last-name')
        billing_details.country = request.POST.get('country')
        billing_details.street_address = request.POST.get('street-address')
        billing_details.city = request.POST.get('city')
        billing_details.postcode = request.POST.get('postcode')
        billing_details.phone = request.POST.get('phone')
        billing_details.email = request.POST.get('email')

        try:
            billing_details.full_clean()
            billing_details.save()  
            return redirect('place_order') 
        except ValidationError as e:
            messages.error(request, f'Error updating billing details: {e}')

    return render(request, 'update_billing_details.html', {'billing_details': billing_details})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def place_order(request):
    billing_details = BillingDetail.objects.filter(user=request.user).last()
    
    if not billing_details:
        return redirect('billing_view')

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')

    unavailable_items = cart_items.filter(rambutan_post__is_available=False)
    if unavailable_items.exists():
        return redirect('cart')

    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 40
    platform_fee = 5
    total = subtotal + delivery_fee + platform_fee
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        order = Order.objects.create(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        if payment_method == 'Razorpay':
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            razorpay_order = client.order.create({
                'amount': int(total * 100), 
                'currency': 'INR',
                'payment_capture': '1'
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            return redirect('razorpay_payment_view', order_number=order.order_number)

        save_order_items(cart_items, order)
        send_order_confirmation_email(request.user, order, total, payment_method)
        cart_items.delete()
        
        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'place_order.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee': platform_fee,
        'total': total,
    })

def razorpay_payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

    amount = int(order.total_amount * 100)

    razorpay_order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
    }

    return render(request, 'razorpay_payment.html', context)

@csrf_exempt
def razorpay_payment_complete(request):
    if request.method == "POST":
        data = request.POST
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client.utility.verify_payment_signature(params_dict)

            order = Order.objects.get(razorpay_order_id=data['razorpay_order_id'])
            order.razorpay_payment_id = data['razorpay_payment_id']
            order.razorpay_signature = data['razorpay_signature']
            order.payment_status = 'completed'
            order.save()

            cart_items = Cart.objects.filter(user=order.user)
            save_order_items(cart_items, order)
            send_order_confirmation_email(order.user, order, order.total_amount, order.payment_method)
            cart_items.delete()

            return redirect('order_detail', order_number=order.order_number)

        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Signature verification failed.")
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order does not exist.")

    return HttpResponseBadRequest("Invalid request.")


def save_order_items(cart_items, order):
    """Save order items and adjust rambutan_post quantities."""
    for item in cart_items:
        rambutan_post = item.rambutan_post
        ordered_quantity = item.quantity

        if rambutan_post.quantity_left < ordered_quantity:
            continue 

        rambutan_post.quantity_left -= ordered_quantity
        if rambutan_post.quantity_left <= 0:
            rambutan_post.is_available = False
        rambutan_post.save()

        OrderItem.objects.create(
            order=order,
            rambutan_post=rambutan_post,
            quantity=ordered_quantity,
            price=item.price
        )

        farmer_details = rambutan_post.farmer
        register_user = farmer_details.user
        OrderNotification.objects.create(
            farmer=register_user,
            order_number=order.order_number,
            item_name=rambutan_post.product,
            quantity=ordered_quantity,
            price=item.price
        )


def send_order_confirmation_email(user, order, total, payment_method):
    """Send order confirmation email."""
    subject = f'Order Confirmation - Order #{order.order_number}'
    message = (
        f'Thank you for your order!\n\n'
        f'Order Number: {order.order_number}\n'
        f'Total Amount: ₹{total}\n'
        f'Payment Method: {payment_method}\n\n'
        f'We will notify you once your items are ready for shipping.'
    )
    recipient_list = [user.username]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    print(f"Sending email to: {user.username}")


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        billing_details = order.billing_detail
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 40
        platform_fee = 5
        total = subtotal + delivery_fee + platform_fee
        
       
    except Order.DoesNotExist:
        return redirect('order')

    return render(request, 'order.html', {
        'order': order,
        'order_items': order_items,
        'billing_details': billing_details,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee': platform_fee,
        'total': total,
        
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    order_details = []

    for order in orders:
        tracking_stages = ["ordered", "packed", "shipped", "out_for_delivery", "delivered"]

        current_time = timezone.now()
        elapsed_time = current_time - order.created_at

        stage_status = {
            'ordered': 'inactive',
            'packed': 'inactive',
            'shipped': 'inactive',
            'out_for_delivery': 'inactive',
            'delivered': 'inactive'
        }

        if elapsed_time < timedelta(days=1):
            stage_status['ordered'] = 'active'
        elif elapsed_time < timedelta(days=2):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
        elif elapsed_time < timedelta(days=4):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
            stage_status['shipped'] = 'active'
        elif elapsed_time < timedelta(days=5):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
            stage_status['shipped'] = 'active'
            stage_status['out_for_delivery'] = 'active'
        else:
            for stage in stage_status:
                stage_status[stage] = 'active'

        if stage_status['delivered'] == 'active' and order.order_status != 'completed':
            order.order_status = 'completed'
            order.save()

        order_items = OrderItem.objects.filter(order=order)
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 0  
        platform_fee = 0  
        total = subtotal + delivery_fee + platform_fee

        delete_allowed = order.created_at >= timezone.now() - timedelta(hours=48)

        order_details.append({
            'order': order,
            'order_items': order_items,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'platform_fee': platform_fee,
            'total': total,
            'delete_allowed': delete_allowed,
            'stage_status': stage_status,
        })

    return render(request, 'order_history.html', {
        'order_details': order_details,
    })


@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Check if the order is eligible for cancellation (created within the last 48 hours)
    if order.created_at >= timezone.now() - timedelta(hours=48):
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            rambutan_post = item.rambutan_post
            rambutan_post.quantity += item.quantity
            rambutan_post.save()

        order.delete()

    return redirect('order_history')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_notifications(request):
    notifications = OrderNotification.objects.all().order_by('-created_at')  
    return render(request, 'order_notifications.html', {'notifications': notifications})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'custom_password_reset.html'  # Your custom template
    email_template_name = 'custom_password_reset_email.html'  # Your custom email template
    subject_template_name = 'custom_password_reset_subject.txt'  # Your custom subject template
    success_url = reverse_lazy('password_reset_done')  # Redirect URL after success

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'custom_password_reset_confirm.html'  # Your custom template
    success_url = reverse_lazy('password_reset_complete')  # Redirect URL after password reset
    

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_farmers = FarmerDetails.objects.count()
    total_rambutan_posts = RambutanPost.objects.count()
    total_orders = Order.objects.filter().count()

    recent_rambutan_posts = RambutanPost.objects.select_related('farmer').order_by('created_at')[:5]

    context = {
        'total_farmers': total_farmers,
        'total_rambutan_posts': total_rambutan_posts,
        'total_orders': total_orders,
        'recent_rambutan_posts': recent_rambutan_posts,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def toggle_user_availability(request, user_id):
    user = get_object_or_404(Registeruser, id=user_id)
    
    user.is_active = not user.is_active
    user.save()
    
    
    status = "available" if user.is_active else "unavailable"
    messages.success(request, f"{user.name} is now set as {status}.")
    
    return redirect('manage_users')

def manage_farmers(request):
    query = request.GET.get('search', '')

    if query:
        farmers = FarmerDetails.objects.filter(
            Q(user__name__icontains=query) | Q(location__icontains=query)
        )
    else:
        farmers = FarmerDetails.objects.all()

    context = {
        'farmers': farmers
    }

    return render(request, 'manage_farmers.html', context)

def edit_farmer(request, farmer_id):
    farmer = get_object_or_404(FarmerDetails, id=farmer_id)
    user = farmer.user

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.contact = request.POST.get('contact')
        user.address = request.POST.get('address')
        user.place = request.POST.get('place')
        user.save()

        farmer.mobile_number = request.POST.get('mobile_number')
        farmer.location = request.POST.get('location')
        farmer.aadhar_number = request.POST.get('aadhar_number')
        farmer.bank_name = request.POST.get('bank_name')
        farmer.account_number = request.POST.get('account_number')
        farmer.ifsc_code = request.POST.get('ifsc_code')
        farmer.save()

        return redirect('manage_farmers')
    
    return render(request, 'edit_farmer.html', {'farmer': farmer, 'user': user})

def delete_farmer(request, farmer_id):
    farmer = get_object_or_404(FarmerDetails, id=farmer_id)
    farmer.delete()
    return redirect('manage_farmers')  

def manage_rambutan_posts(request):
    query = request.GET.get('search', '')

    if query:
        rambutan_posts = RambutanPost.objects.filter(
            Q(farmer__user__name__icontains=query) | Q(tree_variety__name__icontains=query)
        )
    else:
        rambutan_posts = RambutanPost.objects.all()

    context = {
        'rambutan_posts': rambutan_posts
    }

    return render(request, 'manage_rambutan_posts.html', context)

def edit_rambutan_post(request, post_id):
    rambutan_post = get_object_or_404(RambutanPost, id=post_id)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=rambutan_post)

        if form.is_valid():
            updated_post = form.save(commit=False) 

            updated_post.farmer = rambutan_post.farmer  

            updated_post.quantity_left = updated_post.quantity

            if form.cleaned_data.get('product') == 'other':
                updated_post.product = request.POST.get('other_product')
            else:
                updated_post.product = form.cleaned_data.get('product')

            updated_post.category = form.cleaned_data.get('category')
            updated_post.is_available = True

            updated_post.save()
            return redirect('manage_rambutan_posts')  
       
    else:
        form = RambutanPostForm(instance=rambutan_post)

    return render(request, 'edit_post_admin.html', {'rambutan_post': rambutan_post, 'form': form})

def delete_rambutan_post(request, post_id):
    post = get_object_or_404(RambutanPost, id=post_id)
    post.delete()
    return redirect('manage_rambutan_posts')  


def view_orders(request):
    search_query = request.GET.get('search', '')

    if search_query:
        orders = Order.objects.filter(
            Q(order_number__icontains=search_query) |
            Q(user__name__icontains=search_query)
        )
    else:
        orders = Order.objects.all()

    context = {
        'orders': orders,
    }
    return render(request, 'view_orders.html', context)

def admin_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'view_order_details.html', {'order': order})

def manage_customers(request):
    """View to display a list of all customers."""
    search_query = request.GET.get('search', '')
    if search_query:
        customers = CustomerDetails.objects.filter(
            user__name__icontains=search_query) | CustomerDetails.objects.filter(location__icontains=search_query)
    else:
        customers = CustomerDetails.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'manage_customer.html', context)

def edit_customer(request, user_id):
    user = get_object_or_404(Registeruser, id=user_id)

    if request.method == 'POST':
        print(user_id)
        user.name = request.POST.get('name')
        user.contact = request.POST.get('contact')
        user.address = request.POST.get('address')
        user.place = request.POST.get('place')
        
        user.save()
        
        return redirect('manage_customers')  

    context = {
        'user': user,
    }
    return render(request, 'edit_customer.html', context)


def delete_customer(request, customer_id):
    """View to delete a customer."""
    customer = get_object_or_404(CustomerDetails, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('manage_customers')
    return render(request, 'confirm_delete_customer.html', {'customer': customer})

User = get_user_model()

def manage_users(request):
    search_query = request.GET.get('search', '')
    if search_query:
        users = User.objects.filter(username__icontains=search_query).order_by('-date_joined')  
    else:
        users = User.objects.all().order_by('-date_joined')  
    
    return render(request, 'manage_users.html', {'users': users})

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.contact = request.POST.get('contact')
        user.address = request.POST.get('address')
        user.role = request.POST.get('role')
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('manage_users')

    return render(request, 'admin/edit_user.html', {'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_users')

@login_required
def view_order_product(request, order_id, product_id):
    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(RambutanPost, id=product_id)

    if product not in order.products.all():
        return render(request, '404.html', status=404)  

    return render(request, 'admin_view_order.html', {
        'order': order,
        'product': product,
    })


