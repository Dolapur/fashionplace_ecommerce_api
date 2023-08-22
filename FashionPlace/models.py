from django.db import models
import uuid
from django.db.models.lookups import IntegerFieldFloatRounding
from  django.conf import settings
import email
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete


# Create your models here.
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default= None, null=True, blank=True)
    last_name = models.CharField(max_length=100, default= None, null=True, blank=True)
    email = models.EmailField(max_length=100, default= None, null=True, blank=True, unique=True)
    
    
    def __str__(self):
        return self.first_name or "Customer"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def CreateCustomer(sender, instance, created, **kwargs):
    if created:
        customer = Customer.objects.create(user=instance)
        customer.first_name = instance.first_name
        customer.last_name = instance.last_name
        customer.email = instance.email
        customer.save()


class Category(models.Model):
    name = models.CharField('Categories', max_length=255)
    slug = models.SlugField('Slug', max_length=255, unique=True, blank=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name =  models.CharField(max_length=100)
    price = models.FloatField(default=10.55)
    image = models.ImageField()
    product_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    category = models.ManyToManyField(Category, related_name='products')
    new_arrivals = models.BooleanField(default=False)
    top_rated= models.BooleanField(default=False)
    trending = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null = True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    completed = models.BooleanField(default=False)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        cartitems = self.items.all()
        total = sum([item.get_total for item in cartitems])
        return total
    
    @property
    def get_cart_item(self):
        cartitems = self.items.all()
        total = sum(item.quantity for item in cartitems)
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product =  models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cartitems', null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(default=0)

    @property
    def get_total(self):
        total = self.quantity * self.product.price
        if total == 0.00:
            self.delete()
        return total

    def __str__(self):
        return self.product.name


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    pending_status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='PAYMENT_STATUS_PENDING')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.pending_status


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name = "items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.product.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    bio = models.TextField()
    picture = models.ImageField(upload_to = 'img', blank=True, null=True)
    
    def __str__(self):
        return self.username

@receiver(post_delete, sender=Profile)
def delete_related_orders(sender, instance, **kwargs):
    user = instance.user
    
    # Delete related orders and items for the user's customer
    orders = Order.objects.filter(owner=user)
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        order_items.delete()
        order.delete()

    # Delete the associated user's customer
    if user.customer:
        user.customer.delete()

    user.delete()