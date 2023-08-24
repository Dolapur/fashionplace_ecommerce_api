from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="FashionPlace Ecommerce API",
      default_version='v1',
      description="FashionPlace Ecommerce API is a comprehensive solution for managing an online fashion store. It offers user authentication and profile management, seamless shopping cart handling, efficient order processing, and detailed data management. This API ensures secure authentication with JWT tokens and provides endpoints for essential e-commerce operations. Additionally, it guarantees data security and cleanup when a user's profile is deleted, the API takes care of cleaning up the associated data, including their shopping cart, cart items, orders, and order items. This feature ensures that your database remains organized and clutter-free, saving you time and effort.",
      contact=openapi.Contact(email="tichiegoju@gmail.com"),
      license=openapi.License(
         name="MIT License",
         url="https://github.com/Dolapur/fashionplace_ecommerce_api/blob/main/LICENSE",
      ),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()

router.register("products", views.ProductViewSet)
router.register("categories", views.CategoryViewSet)
router.register("carts", views.CartViewSet)
router.register("profile", views.ProfileViewSet)
router.register("orders", views.OrderViewSet, basename="orders")


cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")



urlpatterns = [
    path("", include(router.urls)),
    path("", include(cart_router.urls)),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]