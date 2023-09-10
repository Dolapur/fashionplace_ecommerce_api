from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from FashionPlace.models import *
from api.serializers import *
from rest_framework.authtoken.models import Token


User = get_user_model()

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)


class CategoryViewSetTestCase(APITestCase):
    def test_list_categories(self):
        category1 = Category.objects.create(name="Category 1", slug="category-1")
        category2 = Category.objects.create(name="Category 2", slug="category-2")

        # Assuming you have defined this URL name in your project's URLs
        url = reverse("category-list")

        # Send a GET request to the list endpoint
        response = self.client.get(url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Deserialize the response data using the CategorySerializer
        serializer = CategorySerializer(Category.objects.all(), many=True)

        # Check that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)


class ProductViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )

    def test_list_products(self):
        # Create a sample category
        category = Category.objects.create(name="Category 1")

        # Create some sample products and associate them with the category
        product1 = Product.objects.create(name="Product 1", price=10)
        product1.category.add(category)  # Use .add() to assign the category
        product2 = Product.objects.create(name="Product 2", price=15)
        product2.category.add(category)  # Use .add() to assign the category

        url = reverse("product-list")
        response = self.client.get(url)
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_product(self):
        # Create a sample category
        category = Category.objects.create(name="Test Category")

        # Create a sample product and associate it with the category
        product = Product.objects.create(name="Test Product", price=20)
        product.category.add(category)  # Use .add() to assign the category

        url = reverse("product-detail", args=[product.pk])
        response = self.client.get(url)
        serializer = ProductSerializer(product)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class CartViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )

    def test_create_cart(self):
        url = reverse("cart-list")
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("id" in response.data)

    def test_retrieve_cart(self):
        cart = Cart.objects.create(customer=self.user.customer)
        url = reverse("cart-detail", args=[cart.id])
        response = self.client.get(url)
        serializer = CartSerializer(cart)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_cart(self):
        cart = Cart.objects.create(customer=self.user.customer)
        url = reverse("cart-detail", args=[cart.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())


class CartItemViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", price=20)
        self.cart = Cart.objects.create(customer=self.user.customer) 

    def test_list_cart_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        url = reverse("cart-items-list", args=[self.cart.id])
        response = self.client.get(url)
        serializer = CartItemSerializer(CartItem.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_cart_item(self):
        url = reverse("cart-items-list", args=[self.cart.id])
        data = {
            "product_id": str(self.product.product_id),
            "quantity": 2,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("id" in response.data)

    def test_update_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        url = reverse("cart-items-detail", args=[self.cart.id, cart_item.id])
        data = {
            "quantity": 3,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 3)

    def test_delete_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        url = reverse("cart-items-detail", args=[self.cart.id, cart_item.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

  
class OrderViewSetTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(name="Test Product", price=20)

    def test_list_orders(self):
        order1 = Order.objects.create(owner=self.user)
        order2 = Order.objects.create(owner=self.user)

        url = reverse("orders-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_order(self):
        customer = Customer.objects.create(user=self.user.customer)
        cart = Cart.objects.create(customer=customer)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        url = reverse("orders-list")
        data = {
            "cart_id": str(cart.id),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("id" in response.data)

    def test_retrieve_order(self):
        order = Order.objects.create(owner=self.user)
        url = reverse("orders-detail", args=[order.id])
        response = self.client.get(url)
        serializer = OrderSerializer(order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_order_status(self):
        order = Order.objects.create(owner=self.user)
        url = reverse("orders-detail", args=[order.id])
        data = {
            "pending_status": False,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["pending_status"])

    def test_delete_order(self):
        order = Order.objects.create(owner=self.user)
        url = reverse("orders-detail", args=[order.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_order_creation_associates_with_user(self):
        customer = Customer.objects.create(user=self.user.customer)
        cart = Cart.objects.create(customer=customer)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        url = reverse("orders-list")
        data = {
            "cart_id": str(cart.id),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.owner, self.user.customer)


class ProfileViewSetTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(name="Test Product", price=20)

    def test_list_profiles(self):
        Profile.objects.create(user=self.user, username="TestUser", bio="Test Bio", address="Test Address")
        url = reverse("profile-list")
        response = self.client.get(url)
        serializer = ProfileSerializer(Profile.objects.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_profile(self):
        url = reverse("profile-list")
        data = {
            "username": "TestUser",
            "bio": "Test Bio",
            "address": "Test Address",
        }
        response = self.client.post(url, data, format="json", HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("id" in response.data)

    def test_retrieve_profile(self):
        profile = Profile.objects.create(user=self.user, username="TestUser", bio="Test Bio", address="Test Address")
        url = reverse("profile-detail", args=[profile.id])
        response = self.client.get(url)
        serializer = ProfileSerializer(profile)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_profile(self):
        # Create a user and associated data
        profile = Profile.objects.create(user=self.user, username="TestUser", bio="Test Bio", address="Test Address")
        customer = Customer.objects.create(user=self.user.customer)
        cart = Cart.objects.create(customer=customer)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        order = Order.objects.create(owner=self.user)
        order_item = OrderItem.objects.create(order=order, product=self.product, quantity=2)

        url = reverse("profile-detail", args=[profile.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Profile.objects.filter(id=profile.id).exists())
        
        # Check that associated data is deleted
        self.assertFalse(Cart.objects.filter(customer=self.user.customer).exists())
        self.assertFalse(CartItem.objects.filter(cart=cart).exists())
        self.assertFalse(Order.objects.filter(owner=self.user.customer).exists())
        self.assertFalse(OrderItem.objects.filter(order=order).exists())


class SignUpViewTestCase(APITestCase):
    def test_signup_user(self):
        url = reverse("signup")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("tokens" in response.data)


class LogInViewTestCase(BaseAPITestCase):
    def test_login_user(self):
        url = reverse("login")
        data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("tokens" in response.data)

    def test_login_invalid_credentials(self):
        url = reverse("login")
        data = {
            "email": "test@example.com",
            "password": "invalidpassword",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)