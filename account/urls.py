from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .tokens import JWTCreateView, JWTRefreshView, JWTVerifyView
from api.views import SignUpView, LogInView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="FashionPlace Ecommerce API",
      default_version='v1',
      description="FashionPlace Ecommerce API is a comprehensive solution for managing an online fashion store, it offers user authentication and profile management, seamless shopping cart handling, efficient order processing, and detailed product management. The API ensures secure authentication with JWT tokens and provides endpoints for essential e-commerce operations.",
      contact=openapi.Contact(email="tichiegoju@gmail.com"),
      license=openapi.License(
         name="MIT License",
         url="https://github.com/Dolapur/fashionplace_ecommerce_api/blob/main/LICENSE",
      ),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LogInView.as_view(), name="login"),
    path("jwt/create/", JWTCreateView.as_view(), name="jwt_create"),
    path("jwt/refresh/", JWTRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", JWTVerifyView.as_view(), name="token_verify"),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]