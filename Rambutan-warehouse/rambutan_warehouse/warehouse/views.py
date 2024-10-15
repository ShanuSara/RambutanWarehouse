import random
from urllib import request
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import FarmerDetailsForm,FarmerDetails,RambutanPostForm,RegisterUserForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  BillingDetail, Cart, CustomerDetails, FarmerDetails, Order, OrderItem, OrderNotification, RambutanPost,Registeruser, Wishlist
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .forms import FarmerDetailsForm, TreeVarietyForm, RambutanPostForm
from django.contrib import messages
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_control



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
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
          
            login(request, user)

            request.session['user_id'] = user.id
            request.session['name'] = user.username
            request.session['role'] = user.role
            if user.is_superuser:  # or user.role == 'admin' if you're using a custom role system
                return redirect('/admin') 
            elif user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            else:
                return render(request, 'login.html', {'error': 'Invalid user role'})
        #else:
            #messages.error(request,message="Invalid Credentials")
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


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def post_rambutan(request):
    try:
        farmer_details = request.user.farmerdetails 
        print(farmer_details)
    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details') 

    if request.method == 'POST':
        print(request.POST)
        form = RambutanPostForm(request.POST,request.FILES)
        if form.is_valid():
            rambutan_post = form.save(commit=False)
            rambutan_post.farmer = farmer_details  
            rambutan_post.quantity_left = rambutan_post.quantity  
            rambutan_post.save()
            return redirect('view_posts')  
    else:
        form = RambutanPostForm()

    return render(request, 'post_rambutan.html', {'form': form ,'farmer_details': farmer_details})

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

            updated_post.is_available = True
            updated_post.save()

            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})

    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})

def update_quantity(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity_left')

        if new_quantity is not None:
            try:
                new_quantity = int(new_quantity)
                post.quantity_left = new_quantity
                post.quantity=new_quantity

                if new_quantity > 0:
                    post.is_available = True
                    #messages.success(request, 'Post is now available.')
                else:
                    post.is_available = False
                   # messages.info(request, 'Post is out of stock.')

                post.save()
                return redirect('view_posts')

            except ValueError:
                messages.error(request, 'Please enter a valid number for quantity.')
        else:
            messages.error(request, 'Quantity cannot be empty.')

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
    farmer_details = get_object_or_404(FarmerDetails, user=request.user)
    
    farmer_posts = RambutanPost.objects.filter(farmer=farmer_details)
    
    order_items = OrderItem.objects.filter(rambutan_post__in=farmer_posts).select_related('order', 'rambutan_post')

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
def products_browse(request):
    products = RambutanPost.objects.all().values('id', 'name', 'variety', 'image', 'price_per_kg', 'created_at', 'description', 'is_available', 'quantity_left')
    
    cart_items = Cart.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)

    for product in products:
        if product['quantity_left'] <= 0:
            product['status_message'] = 'Out of Stock'
        elif not product['is_available']:
            product['status_message'] = 'Unavailable'

    context = {
        'products': products,
    }
    return render(request, 'shop.html', context)

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
            defaults={'price': rambutan_post.price_per_kg} 
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
            messages.success(request, 'Billing details updated successfully.')
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
    platform_fee = 10
    # discount = 100
    total = subtotal + delivery_fee + platform_fee

    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        order = Order.objects.create(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        for item in cart_items:
            rambutan_post = item.rambutan_post
            ordered_quantity = item.quantity

            if rambutan_post.quantity_left < ordered_quantity:
                return redirect('cart')

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
                item_name=rambutan_post.name,
                quantity=ordered_quantity,
                price=item.price
            )

        cart_items.delete()

        subject = 'Order Confirmation - Order #{}'.format(order.order_number)
        message = (
            f'Thank you for your order!\n\n'
            f'Order Number: {order.order_number}\n'
            f'Total Amount: ₹{total}\n'
            f'Payment Method: {payment_method}\n\n'
            f'We will notify you once your items are ready for shipping.'
        )
        recipient_list = [request.user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'place_order.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee' : platform_fee,
        # 'discount': discount,
        'total': total,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        order_items = OrderItem.objects.filter(order=order)  
        
        billing_details = order.billing_detail
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 0 
        discount = 0     
        total = subtotal + delivery_fee - discount

    except Order.DoesNotExist:
        return redirect('order')

    return render(request, 'order.html', {
        'order': order,
        'order_items': order_items,
        'billing_details': billing_details,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'discount': discount,
        'total': total,
    })

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'order_history.html', {
        'orders': orders
    })

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_notifications(request):
    notifications = OrderNotification.objects.all().order_by('-created_at')  # Fetching all notifications
    return render(request, 'order_notifications.html', {'notifications': notifications})


from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class CustomPasswordResetView(PasswordResetView):
    template_name = 'custom_password_reset.html'  # Your custom template
    email_template_name = 'custom_password_reset_email.html'  # Your custom email template
    subject_template_name = 'custom_password_reset_subject.txt'  # Your custom subject template
    success_url = reverse_lazy('password_reset_done')  # Redirect URL after success

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'custom_password_reset_confirm.html'  # Your custom template
    success_url = reverse_lazy('password_reset_complete')  # Redirect URL after password reset
    

