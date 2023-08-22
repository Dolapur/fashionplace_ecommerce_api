import json
import uuid
import stripe
from .models import *
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from  .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.conf import settings


# Create your views here.
def home(request):
    new_arrivals = Product.objects.filter(new_arrivals=True)
    top_rated = Product.objects.filter(top_rated=True)
    trending = Product.objects.filter(trending=True)

    return render(request, 'home.html', {
        'new_arrivals': new_arrivals,
        'top_rated': top_rated,
        'trending': trending,
    })


def all_products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {
        'products': products
    })


def all_category(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'category.html', {
        'category': category,
        'products': products
    })


def search_product(request):
    product_name = request.POST.get('product_name')
    searched_products = Product.objects.filter(name__icontains=product_name)
    return render(request, 'search.html', {
        'searched_products': searched_products,
    })


def cart(request):
    return render(request, 'cart.html', {})


def updatecart(request):
    data = json.loads(request.body)
    product_id = data['product_id']
    action = data['action']
    product = Product.objects.get(product_id=product_id)

    if request.user.is_anonymous:
        cart = Cart.objects.get(session_id=request.session['nonuser'], completed=False)
    elif request.user.is_authenticated:
        cart_queryset = Cart.objects.filter(customer=request.user.customer, completed=False)
        cart = cart_queryset.first() if cart_queryset.exists() else Cart.objects.create(customer=request.user.customer, completed=False)

    cartitems = CartItem.objects.filter(cart=cart, product=product)
    if cartitems.exists():
        cartitems = cartitem.first()  
        if action == 'add':
            cartitems.quantity += 1
            cartitems.save()
    else:
        cartitems = CartItem.objects.create(cart=cart, product=product, quantity=1)


    msg = {
        'quantity': cart.get_cart_item
    }

    return JsonResponse(msg)


def updatequantity(request):
    data = json.loads(request.body)
    quantity = int(data['in_val'])
    product_id = data['p_id']
    product = Product.objects.get(product_id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(customer=request.user.customer, completed=False)
    if request.user.is_anonymous:
        cart = Cart.objects.get(session_id=request.session['nonuser'], completed=False)

    cartitems = CartItem.objects.filter(product=product, cart=cart)
    if cartitems.exists():
        cartitem = cartitems.first() 
        cartitem.quantity = quantity

        if cartitem.quantity == 0:
            cartitem.delete()
        else:
            cartitem.save()
    else:
        cartitems = CartItem.objects.create(product=product, cart=cart, quantity=quantity)

    msg = {
        'subtotal': cartitem.get_total,
        'grandtotal': cart.get_cart_total,
        'quantity': cart.get_cart_item
    }

    return JsonResponse(msg)

def register_page(request):
    if request.method == 'POST':
        register_form = CreateUserForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.save()

            session_id = str(uuid.uuid4())  
            if 'nonuser' in request.session:
                session_id = request.session['nonuser']
                del request.session['nonuser']
            request.session['nonuser'] = session_id
            request.session.save()

            first_name = register_form.cleaned_data.get('first_name')
            last_name = register_form.cleaned_data.get('last_name') 
            email = register_form.cleaned_data.get('email')
            customer = Customer.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)
            customer.save()

            cart = Cart.objects.filter(session_id=session_id, completed=False).first()
            if cart:
                cart.session_id = session_id
                cart.customer = customer
                cart.save()

            messages.info(request, "Account Created Successfully!")
            login(request, user)
            return redirect('checkout')
        else:
            messages.error(request, "Registration Failed")
    else:
        register_form = CreateUserForm()

    return render(request, 'register.html', {'register_form': register_form})


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)

            if 'nonuser' in request.session:
                nonuser_cart = Cart.objects.filter(session_id=request.session['nonuser'], completed=False).first()

                # Check if the user has a customer instance
                if hasattr(request.user, 'customer'):
                    user_cart = Cart.objects.filter(customer=request.user.customer, completed=False).first()
                else:
                    # Create a customer instance for the user if it doesn't exist
                    customer = Customer.objects.create(user=request.user)
                    user_cart = Cart.objects.create(customer=customer, session_id=request.session['nonuser'])


                if nonuser_cart and user_cart:
                    nonuser_cart_items = nonuser_cart.items.all()
                    for nonuser_cart_item in nonuser_cart_items:
                        existing_cart_item = user_cart.items.filter(product=nonuser_cart_item.product).first()
                        if existing_cart_item:
                            existing_cart_item.quantity += nonuser_cart_item.quantity
                            existing_cart_item.save()
                        else:
                            nonuser_cart_item.cart = user_cart
                            nonuser_cart_item.save()
                            
                    nonuser_cart.delete()
                
                user_cart.save()

                del request.session['nonuser']
                request.session.save()

            return redirect('checkout')
        else:
            messages.info(request, "Invalid Credentials")

    return render(request, 'login.html')


@login_required(login_url='login')
def checkout(request):
    return render(request, 'checkout.html')


def payment(request, pk):
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        cart_id = pk
        cart = Cart.objects.get(id=cart_id)
        token = request.POST.get('stripeToken')

        cart_total = cart.get_cart_total

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            charge = stripe.Charge.create(
                amount=int(cart_total * 100),
                currency='usd',
                source=token,
            )
            if charge.status == 'succeeded':
                cart.completed = True
                cart.save()
                messages.success(request, "Payment made successfully")
                return redirect("home")
        except stripe.error.CardError as e:
            error = e.user_message
            return render(request, 'checkout.html', {'error': error})
    context = {
        'publishable_key': publishable_key,
    }
    return render(request, 'checkout.html', context)

    return render(request, 'checkout.html', context)



def logout_page(request):
    logout(request)
    return redirect('home')