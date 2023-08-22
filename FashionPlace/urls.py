from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products', views.all_products, name='products'),
    path('category/<str:slug>', views.all_category, name='category'),
    path('search', views.search_product, name='product_search'),
    path('cart', views.cart, name='cart'),
    path('updatecart', views.updatecart),
    path('updatequantity', views.updatequantity),
    path('checkout', views.checkout, name='checkout'),
    path('register', views.register_page, name = 'register'),
    path('login', views.login_page, name = 'login'),
    path('payment/<str:pk>', views.payment, name='payment'),
    path('logout', views.logout_page, name = 'logout')
]