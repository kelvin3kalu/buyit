from django.shortcuts import render,redirect
from .models import Product,Category,CartItem,Order,OrderItem
from .product import Podu
from django.contrib.auth import authenticate,login,logout,user_logged_in
from .reigister import Register, EditProfileForm
from django.contrib.auth.decorators import login_required
from .decorate import group_required
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from .models import ContactMessage
from .forms import ContactForm
from django.core.mail import BadHeaderError
from django.contrib import messages
from django.conf import settings
import socket

import requests


# Create your views here.
def home(request):
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')


def faqs(request):
    return render(request,'faqs.html')

def terms(request):
    return render(request,'terms.html')

def notlog(request):
    messages.error(request, "You must log in before accessing this page.")
    return redirect('login')

from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm  # Assuming you have this form

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Build the full message content
            full_message = f"""
            New contact form submission from BuyIt:

            Name: {name}
            Email: {email}

            Subject: {subject}

            Message:
            {message}
            """

            try:
                send_mail(
                    subject=f"Contact Form - {subject}",
                    message=full_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],  # ✅ sends to you
                    fail_silently=False,
                    reply_to=[email],  # ✅ lets you click "Reply" to message the user
                )
                messages.success(request, "Your message was sent successfully.")
                return redirect('contact')
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('settings')
            except TimeoutError:
                messages.error(request, "Login timed out. Please try again.")
            except socket.gaierror as e:
                if e.errno == 11001:
                    messages.error(request,"Please check your internet connection")
                else:
                    messages.error(request,f" Network error occurred: {e}")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = Register()
    return render(request, 'register.html', {'form': form})


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('settings')
            except TimeoutError:
                messages.error(request, "Login timed out. Please try again.")
            except socket.gaierror as e:
                if e.errno == 11001:
                    messages.error(request,"Please check your internet connection")
                else:
                    messages.error(request,f" Network error occurred: {e}")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                print(user)
                login(request,user)
                messages.success(request,'login successfull')
                return redirect('product_list')
            # except TimeoutError:
            #     messages.error(request, "Login timed out. Please try again.")
            # except socket.gaierror as e:
            #     if e.errno == 11001:
            #         messages.error(request,"Please check your internet connection")
            #     else:
            #         messages.error(request,f" Network error occurred: {e}")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Invalid Username or Password")
    return render(request,'login.html')

@group_required('admin')
def product(request):
    if request.method == 'POST':
        form = Podu(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = Podu()
    return render(request, 'addproduct.html', {'form': form})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'category_products.html', {
        'category': category,
        'products': products
    })



def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')  # Get the search input
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    categories = Category.objects.all()

    # Start with all products or filtered by category
    if category_id:
        products = Product.objects.filter(category__id=category_id)
    else:
        products = Product.objects.all()

    # Filter by search query if provided
    if search_query:
        products = products.filter(name__icontains=search_query)

    return render(request, 'products.html', {
        'User':user,
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'search_query': search_query,  # Send search input to template
    })



def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
@group_required('admin')
def product_edit(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = Podu(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = Podu(instance=product)
    return render(request, 'product_edit.html', {'form': form, 'product': product})


@login_required
@group_required('admin')
def product_delete(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_delete.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('cart') 

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, cart_item_id):
    item = get_object_or_404(CartItem, id=cart_item_id)
    item.delete()
    return redirect('cart')

def logout_user(request):
    logout(request)
    return redirect('login')
name = 'beauty'
stupid = 'beauty'
if name == stupid:
    print(f'{name} is stupid')



import uuid

@login_required
def initialize_payment(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    
    if total == 0:
        messages.error(request, "Cart is empty.")
        return redirect('cart')

    amount = int(total * 100)  # Convert to Kobo
    reference = str(uuid.uuid4())  # Unique reference

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": request.user.email,
        "name": request.user.username,
        "amount": amount,
        "reference": reference,
        "callback_url": request.build_absolute_uri('/payment/callback/')
    }

    try:
        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        result = response.json()

        if result.get("status") is True:
            return redirect(result["data"]["authorization_url"])
        else:
            messages.error(request, "Failed to initiate payment.")
            return redirect('cart')

    except Exception as e:
        messages.error(request, f"Error connecting to payment gateway: {e}")
        return redirect('cart')


@login_required
def payment_callback(request):
    reference = request.GET.get('reference')

    if not reference:
        messages.error(request, "No payment reference provided.")
        return redirect('cart')

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        result = response.json()

        if result.get("status") and result["data"]["status"] == "success":
            cart_items = CartItem.objects.filter(user=request.user)

            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect('cart')

            # Total amount from cart
            total = sum(item.total_price() for item in cart_items)

            # Step 1: Save the Order
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                reference=reference
            )

            # Step 2: Save each cart item as an OrderItem
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            # Step 3: Clear the cart
            cart_items.delete()

            messages.success(request, "Payment successful! Order saved.")
            return redirect('product_list')

        else:
            messages.error(request, "Payment verification failed or was cancelled.")
            return redirect('cart')

    except Exception as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'orders': orders})

@login_required
def remove_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, "Order deleted successfully.")
    return redirect('order_history')

@login_required
def clear_order_history(request):
    Order.objects.filter(user=request.user).delete()
    messages.success(request, "Order history cleared successfully.")
    return redirect('order_history')

from django.shortcuts import render

def payment_success(request):
    return render(request, "payment_success.html")

def payment_cancelled(request):
    return render(request, "payment_cancelled.html")
