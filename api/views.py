
from FashionPlace.models import *
from  .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.request import Request
from account.tokens import  get_tokens_for_user
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404


class CategoryViewSet(ListModelMixin, GenericViewSet):
    """
    A ViewSet for managing Category viewset.

    Supported HTTP methods: GET.

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Get a list of all categories.",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    A ViewSet for managing Product viewset.

    Supported HTTP methods: GET, DELETE.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="List all products",
        operation_description="Get a list of all products.",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a products by ID",
        operation_description="Retrieve a products with the given ID.",
        responses={200: CategorySerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price']
    pagination_class = PageNumberPagination


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    """
    A ViewSet for managing Cart viewset.

    Supported HTTP methods: GET, POST, DELETE.
    """

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create a cart",
        operation_description="Create a cart with the given data.",
        responses={201: CartSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Retrieve a cart by ID",
        operation_description="Retrieve a cart with the given ID.",
        responses={200: CartSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a cart by ID",
        operation_description="Delete a cart with the given ID.",
        responses={204:"No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CartItemViewSet(ModelViewSet):
    """
    A ViewSet for managing Cartitems.

    Supported HTTP methods: GET, POST, PATCH, DELETE.

    Attributes:
        http_method_names: The list of allowed HTTP methods for this ViewSet.

    Methods:
        get_queryset(): Returns the queryset of CartItem objects filtered by cart_id.
        get_serializer_class(): Returns the appropriate serializer class based on the request method.
        get_serializer_context(): Returns the serializer context with cart_id as a parameter.

    """

    http_method_names = ["get", "post", "patch", "delete"]

    permission_classes = [AllowAny]

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    @swagger_auto_schema(
        operation_summary="List Cartitems",
        operation_description="Retrieve a list of Cartitems for a specific cart.",
        responses={200: CartItemSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @swagger_auto_schema(
        operation_summary="Add a Cartitem to cart",
        operation_description="Add a new Cartitem to the cart.",
        responses={201: CartItemSerializer()},
        request_body=AddCartItemSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = AddCartItemSerializer(data=request.data, context={"cart_id": kwargs["cart_pk"]})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @swagger_auto_schema(
        operation_summary="Retrieve a Cartitem from a cart",
        operation_description="Retrieve details of a specific Cartitem in the cart.",
        responses={200: CartItemSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary="Partial Update of a Cartitem in a cart",
        operation_description="Update specific fields of a Cartitem in the cart.",
        responses={200: CartItemSerializer()},
        request_body=UpdateCartItemSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateCartItemSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a Cartitem in a cart",
        operation_description="Delete a specific Cartitem in a cart.",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    # """
    # A ViewSet for managing Order viewset.

    # Supported HTTP methods: GET, PATCH, POST, DELETE.

    # """

    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "patch", "post", "delete", "options", "head"]

    @swagger_auto_schema(
        operation_summary="List customer orders",
        operation_description="Retrieve a list of orders for the authenticated user.",
        responses={200: OrderSerializer(many=True), 400: "Bad Request", 403: "Forbidden", 404: "Not Found"}
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            raise PermissionDenied("Authentication required to access orders.")
        if user.is_staff:
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(owner=user)

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve the customer order",
        operation_description="Retrieve a list of Cartitems for the authenticated customer.",
        responses={200: OrderSerializer(many=True), 400: "Bad Request", 403: "Forbidden", 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial Update of a Customer Order ",
        operation_description="Update specific fields of a Customer Order.",
        request_body=UpdateOrderSerializer,
        responses={200: OrderSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        permission_classes = [IsAdminUser]
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Customer Order",
        operation_description="Delete a specific Customer Order.",
        responses={
            204: "No Content",
            404: "Not Found",
            403: "Forbidden",
        }
    )
    def destroy(self, request, *args, **kwargs):
        user = request.user  
        order = get_object_or_404(Order, pk=kwargs['pk'], owner=user)

        for item in order.items.all():
            item.delete()

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Create an order",
        operation_description="Create an order with the given data.",
        request_body=CreateOrderSerializer,
        responses={201: OrderSerializer(), 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs): 
        serializer = CreateOrderSerializer(data=request.data, context={"user_id": request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        elif self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Order.objects.none()  
        elif user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(owner=user)
       
        
class ProfileViewSet(ModelViewSet):
    """
    A ViewSet for managing Cartitems.

    Supported HTTP methods: GET, POST, PATCH, DELETE.

    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    http_method_names = ["get", "put", "post", "delete"]

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List Customer Profile",
        operation_description="Retrieve a list of authenicated customer profile.",
        responses={200: ProfileSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            raise PermissionDenied("Authentication required to access profile")
        if user.is_staff:
            queryset = Profile.objects.all()
        else:
            queryset = Profile.objects.filter(customer=user.customer)

        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a Profile",
        operation_description="return a profile for a customer.",
        responses={201: ProfileSerializer(),
            403: "Forbidden",
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.user

        if Profile.objects.filter(user=user).exists():
            raise PermissionDenied("A profile already exists for this user.")

        username = request.data["username"]
        bio = request.data["bio"]
        picture = request.data["picture"]

        profile = Profile.objects.create(user=user, username=username, bio=bio, picture=picture)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Retrieve a Customer Profile",
        operation_description="Retrieve details of a Customer Profile.",
        responses={200: ProfileSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update of a Customer Profile",
        operation_description="Update specific fields of a Customer Profile.",
        responses={200: ProfileSerializer()}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a Customer Profile",
        operation_description="Delete a specific Customer Profile.",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        user = request.user
        profile = self.get_object()
        if not user.is_staff and profile.user != user:
            raise PermissionDenied("You do not have permission to delete this profile")
            
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="SignUp a new user",
        operation_description="Create a new user account by providing the required user information.",
        request_body=SignUpSerializer,
        responses={
            201: "User Created Successfully",
            400: "Bad Request - Invalid input data"
        }
    )
    def post(self, request: Request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            response_data = {
                "message": "User Created Successfully",
                "data": serializer.data,
                "tokens": tokens
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogInView(APIView):
    """
    A View to handle user login and retrieve JWT tokens.

    Supported HTTP methods: POST, GET.

    """

    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Login authenticated users",
        operation_description="Login a user with the provided email and password, and return JWT tokens.",
        responses={
            200: "Login Successful",
            401: "Invalid email or password",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
            required=["email", "password"],
        ),
    )
    def post(self, request):
        """
        Login a user with the provided email and password, and return JWT tokens.

        """
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user is not None:
            tokens = get_tokens_for_user(user)
            response_data = {
                "message": "Login Successful",
                "tokens": tokens
            }
            return Response(data=response_data, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_summary="Get User Info",
        operation_description="Get information about the current authenticated user and their authentication status.",
        responses={200: "User information"},
    )
    def get(self, request):
        """
        Get information about the current authenticated user and their authentication status.
        """
        response_data = {
            "user": str(request.user),
            "auth": str(request.auth)
        }
        return Response(data=response_data, status=status.HTTP_200_OK)