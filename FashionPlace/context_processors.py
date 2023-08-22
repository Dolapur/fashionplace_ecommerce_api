from FashionPlace.models import *
from django.contrib.sessions.models import Session
import uuid

def category_links(request):
    category = Category.objects.all()
    return {'categories': category}


def cart_render(request):
    cart = Cart.objects.none()
    cartitems = CartItem.objects.none()
    try:
        cart = Cart.objects.get(customer=request.user.customer, completed=False)
        cartitems = CartItem.objects.filter(cart=cart)
    except:
        if request.user.is_anonymous:
            try:
                cart = Cart.objects.get(session_id = request.session['nonuser'], completed=False)
                cartitems = CartItem.objects.filter(cart=cart)
            except:
                request.session['nonuser'] = str(uuid.uuid4())
                cart = Cart.objects.create(session_id = request.session['nonuser'], completed=False)
                cartitems = CartItem.objects.filter(cart=cart).first()
    return {'cart': cart, 
        'cartitems': cartitems
    }




