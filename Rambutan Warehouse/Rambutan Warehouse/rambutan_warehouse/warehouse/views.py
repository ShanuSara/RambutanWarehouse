from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerDetailsForm, FarmerDetailsForm,FarmerDetails,RambutanPostForm,RegisterUserForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomerDetails, FarmerDetails, RambutanPost,Registeruser, Wishlist
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .forms import FarmerDetailsForm, TreeVarietyForm, RambutanPostForm

def farmer_details(request):
    try:
       
        farmer_details = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        farmer_details = None

    if request.method == 'POST':
        
        form = FarmerDetailsForm(request.POST, request.FILES, instance=farmer_details)
        if form.is_valid():
            farmer_profile = form.save()
            farmer_profile.user = request.user
             
            farmer_profile.save()
            messages.success(request, "Your profile has been updated successfully." if farmer_details else "Profile created successfully.")
            return redirect('farmer_dashboard')  
    else:
        form = FarmerDetailsForm(instance=farmer_details)

    return render(request, 'farmer_details.html', {
        'form': form
    })

def create_farmer_details(request):
    if request.method == 'POST':
        form = FarmerDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')
    else:
        form = FarmerDetailsForm()
    return render(request, 'forms.html', {'form': form})

def create_tree_variety(request):
    if request.method == 'POST':
        form = TreeVarietyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')    
    else:
        form = TreeVarietyForm()
    return render(request, 'forms.html', {'form': form})

def create_rambutan_post(request):
    if request.method == 'POST':
        form = RambutanPostForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')
    else:
        form = RambutanPostForm()
    return render(request, 'forms.html', {'form': form})

def contact(request):
    return render(request,'contact.html')

def index(request):
    if request.method =='POST':
        pass
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .models import Registeruser

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            # Get the email from the form
            email = form.cleaned_data.get('email')
            
            # Check if the email is already registered
            if Registeruser.objects.filter(email=email).exists():
                print('user already existes')
                messages.info(request, "Email is already registered. Please log in.")
                return redirect('login')  # Redirect to the login page
            
            # Create a new user instance without saving
            user = form.save(commit=False)
            # Hash the password and set it
            user.password = make_password(form.cleaned_data.get('password'))
            # Save the new user
            user.save()
            
            messages.success(request, "Registration successful! You can now log in.")
            print('redirect to login')
            return redirect('login')  # Redirect to the login page
        else:
            print(form.errors)
            print('invalid data')
    form = RegisterUserForm()
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
            if user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            else:
                return render(request, 'login.html', {'error': 'Invalid user role'})
        else:
            return HttpResponse('authetication failed')
    return render(request, 'login.html')

@login_required
def farmer_dashboard(request):
    try:
        user = Registeruser.objects.get(username=request.user.username,role='farmer')
    except Registeruser.DoesNotExist:
        return render(request, '404.html')  
    return render(request, 'farmer_dashboard.html', {'farmer': user})

@login_required
def post_rambutan(request):
    return render(request, 'post_rambutan.html')

@login_required
def view_posts(request):
    return render(request, 'view_posts.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 

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
            rambutan_post.save()
            return redirect('view_posts')  
        else:
            print(form.errors)
    else:
        form = RambutanPostForm()

    return render(request, 'post_rambutan.html', {'form': form})

@login_required
def view_posts(request):
    user = request.user  

    try:
        farmer_details = user.farmerdetails  

        posts = RambutanPost.objects.filter(farmer=farmer_details)

    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details')  

    context = {
        'posts': posts,
        'user': user  
    }

    print(context)

    return render(request, 'view_posts.html', context)

def redirect_post_rambutan(request):
    return redirect('post_rambutan') 

@login_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html', {'cart': cart})

@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')

@login_required
def products_browse(request):
    products = RambutanPost.objects.values('name', 'variety', 'image', 'price_per_kg', 'created_at', 'description')
    
    context = {
        'products': products
    }
    return render(request, 'shop.html', context)

@login_required
def wishlist(request):
    # wishlist_items = Wishlist.objects.filter(user=request.user)
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('rambutan_post')

    wishlists = RambutanPost.objects.filter(id__in=[item.rambutan_post_id for item in wishlist_items])

    # wishlists = []
    # for item in wishlist_items:
    #     print(item.rambutan_post_id)
    #     wishlists.append(RambutanPost.objects.filter(id=item.rambutan_post_id))

    # print(wishlists)

    # print(wishlist_items)

    return render(request, 'wishlist.html', {'wishlist_items': wishlists})


@login_required
def cart(request):
    return render(request, 'cart.html')

@login_required
def checkout(request):
    return render(request, 'checkout.html')

@login_required
def blog(request):
    return render(request, 'blog.html')
    

@login_required
def customer_details(request):
    if request.method == 'POST':

        address = request.POST.get('address')
        mobile_number = request.POST.get('mobile_number')
        location = request.POST.get('location', '')
        total_orders = int(request.POST.get('total_orders', 0))
        total_amount_spent = float(request.POST.get('total_amount_spent', 0.00))

        
        CustomerDetails.objects.create(
            user=request.user,
            address=address,
            mobile_number=mobile_number,
            location=location,
            total_orders=total_orders,
            total_amount_spent=total_amount_spent,
        )

        return redirect('profile_view')  

    return render(request, 'customer_details.html') 

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import RambutanPost, Wishlist

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        print(request.POST)
        # product_name = request.POST.get('product_name')  # Get the product name from the form
        # product = get_object_or_404(RambutanPost, name=product_name)  # Fetch the product

        product_id = request.POST.get('product_name')

# Check if product_id is not None before converting
        if product_id:
            
            product_id = int(product_id) 
            # Convert the string to an integer
            
              
 # Get the product name from the form
        product = get_object_or_404(RambutanPost, id=product_id)  # Fetch the product

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            rambutan_post=product  # Store the product name in wishlist
        )
        if created:
            messages.success(request, 'Product added to wishlist.')
        else:
            messages.info(request, 'Product is already in your wishlist.')

        return redirect('wishlist')  # Redirect to the wishlist page

    return redirect('home')  # Fallback 


@login_required
def product_single(request):
    return render(request, 'product-single.html')




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomerDetails

@login_required
def profile_view(request):
    # Try to get the customer details for the logged-in user
    try:
        customer_details = request.user.customerdetails
    except CustomerDetails.DoesNotExist:
        # If the user does not have customer details, redirect to the form
        return redirect('customer_details')  # Make sure to define this URL in your urls.py
    context = {
        'customer_details': customer_details,
    }
    # If customer details exist, render the profile view
    return render(request, 'customer_profile.html', context)













































from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .forms import RambutanPostForm
from .models import RambutanPost

@login_required
def update_post(request):
    # Get the `created_at` from the query parameter
    created_at_str = request.GET.get('created_at')
    
    # Try parsing the created_at using the correct format for "Sept. 20, 2024, 3:49 p.m."
    try:
        created_at = datetime.strptime(created_at_str, '%b. %d, %Y, %I:%M %p')
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid date format. It must be 'MMM. DD, YYYY, H:MM AM/PM'")

    # Get the post for the current user based on the parsed `created_at`
    post = get_object_or_404(RambutanPost, user=request.user, created_at=created_at)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('view_posts')  # Redirect to the posts view after updating
    else:
        form = RambutanPostForm(instance=post)

    return render(request, 'update_post.html', {'form': form})


from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import RambutanPost

from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import RambutanPost

@login_required
def delete_post(request):
    # Get the `created_at` from the query parameter
    created_at_str = request.GET.get('created_at')
    
    # Try parsing the `created_at` using the correct format for "Sept. 20, 2024, 3:49 p.m."
    try:
        created_at = datetime.strptime(created_at_str, '%b. %d, %Y, %I:%M %p')
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid date format. It must be 'MMM. DD, YYYY, H:MM AM/PM'")

    # Get the post for the current user based on the parsed `created_at`
    post = get_object_or_404(RambutanPost, user=request.user, created_at=created_at)

    if request.method == 'POST':
        post.delete()
        return redirect('view_posts')  # Redirect to the list of posts after deletion

    return render(request, 'confirm_delete.html', {'post': post})

from datetime import datetime

def update_post(request):
    created_at = request.GET.get('created_at')
    try:
        # Try parsing the date in the expected format
        created_at = datetime.strptime(created_at, '%b. %d, %Y, %I:%M %p')
        # Further logic to handle post update
    except ValueError:
        return HttpResponseBadRequest('Invalid date format. It must be "MMM. DD, YYYY, H:MM AM/PM"')

''' 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import RambutanPost, Wishlist
from .forms import WishlistForm

@login_required
def add_to_wishlist(request, product_name):
    # Fetch the product by name instead of id
    product = get_object_or_404(RambutanPost, name=product_name)
    
    if request.method == 'POST':
        # Form submission to add product to wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            rambutan_post=product
        )
        if created:
            messages.success(request, 'Product added to wishlist.')
        else:
            messages.info(request, 'Product is already in your wishlist.')
        return redirect('wishlist')  # Redirect to the wishlist page

    return redirect('shop')  # Redirect back to the shopping page if GET request
'''