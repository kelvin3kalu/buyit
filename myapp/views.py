from django.shortcuts import render,redirect
from .models import Product, Category,CartItem
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


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(
                    subject=f"Message from {name}: {subject}",
                    message=message,
                    from_email=email,
                    recipient_list=['my_email@gmail.com'],
                )
                return redirect('contact')
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
                return redirect('contact')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})




def register(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = Register()
    return render(request, 'register.html', {'form': form})


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('settings')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(user)
            login(request,user)
            messages.success(request,'login successfull')
            return redirect('product_list')
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


