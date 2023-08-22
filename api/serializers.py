from FashionPlace.models import *
from rest_framework import serializers
from django.db import transaction
from rest_framework.validators import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ["id", "first_name", "last_name",  "email", "password"]

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs["email"]).exists()
        if email_exists:
            raise ValidationError("Email has already been used")
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def to_representation(self, instance):
        # Exclude the 'password' field from the response
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    class Meta:
        model = Product
        fields = '__all__'

    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id","name", "price"]
        
        
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False)
    sub_total = serializers.SerializerMethodField( method_name="cart_quantity")
    class Meta:
        model= CartItem
        fields = ["id", "cart", "product", "quantity", "sub_total"]
        
    def cart_quantity(self, cartitem:CartItem):
        return format(cartitem.quantity * cartitem.product.price, '.2f')


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value
    
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cartitem = CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cartitem.quantity += quantity
            
            if cartitem.quantity <= 0:
                cartitem.delete()
                raise serializers.ValidationError("Cartitem cannot be zero or negative")
            cartitem.save()

            self.instance = cartitem
        except:
            if quantity > 0:
                self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            else:
                raise serializers.ValidationError("Quantity cannot be zero or negative")

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name='cart_total')
    
    class Meta:
        model = Cart
        fields = ["id", "items", "grand_total"]
           
    def cart_total(self, cart: Cart):
        items = cart.items.all()
        total = sum([item.quantity * item.product.price for item in items])
        return format(total, '.2f')


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem 
        fields = ["id", "product", "quantity"]
        


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order 
        fields = ['id', "placed_at", "pending_status", "owner", "items"]
        

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart_id is invalid")
        
        elif not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Sorry your cart is empty")
        
        return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            order = Order.objects.create(owner_id = user_id)
            cartitems = CartItem.objects.filter(cart_id=cart_id)
            orderitems = [
                OrderItem(order=order, product=item.product, quantity=item.quantity)
            for item in cartitems
            ]
            OrderItem.objects.bulk_create(orderitems)
            # Cart.objects.filter(id=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = ["pending_status"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "username", 'bio', "picture"]


