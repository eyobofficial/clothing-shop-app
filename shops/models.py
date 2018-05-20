from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse


def get_deleted_user():
    return get_user_model().objects.get_or_create(username='Deleted')[0]


class CustomUser(AbstractUser):
    pass


class Base(models.Model):
    """
    Base abstract model for all other models to inherit from
    """
    created_at = models.DateTimeField(
        'Created date',
        auto_now_add=True,
        help_text='Record created date and time.'
    )
    updated_at = models.DateTimeField(
        'Modified date',
        auto_now=True,
        help_text='Record last modified date and time'
    )

    class Meta:
        abstract = True


class Shop(Base):
    """
    Models a virtual shop
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    logo = models.ImageField(
        upload_to='shops/logo/',
        null=True, blank=True
    )
    description = models.TextField('Short description', blank=True)

    class Meta:
        get_latest_by = ['updated_at', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:shop-detail', args=[str(self.pk)])


class Catagory(Base):
    """
    Models Product Catagory
    Example: Dress, Shoes, Leather etc...
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField('Short description', blank=True)

    class Meta:
        get_latest_by = ['-updated_at', ]

    def __str__(self):
        self.name

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:catagory-detail', args=[str(self.pk)])


class Tag(Base):
    """
    Models a product Tag
    Example: leather, oldies, modern, jano etc...
    """
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Product(Base):
    """
    Models a Product
    """
    GENDER_OPTIONS = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    AGE_OPTIONS = (
        ('A', 'Adults'),
        ('K', 'Kids'),
    )
    shop = models.ForeignKey(
        Shop,
        related_name='products',
        on_delete=models.CASCADE,
    )
    catagory = models.ForeignKey(
        Catagory,
        related_name='products',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(
        Tag,
        blank=True, related_name='products',
    )
    gender = models.CharField(max_length=1, choices=GENDER_OPTIONS)
    age = models.CharField(max_length=1, choices=AGE_OPTIONS)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_on_sale = models.BooleanField('On sale', default=False)
    is_featured = models.BooleanField('Featured', default=False)
    thumbnail = models.ImageField(upload_to='shops/products/')
    publish = models.BooleanField(
        default=True,
        help_text='Publish product to the public'
    )

    class Meta:
        order_with_respect_to = 'shop'
        get_latest_by = ['-updated_at', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:product-detail', args=[str(self.pk)])


class ProductPicture(Base):
    product = models.ForeignKey(
        Product,
        related_name='pictures',
        on_delete=models.CASCADE
    )
    picture = models.ImageField(
        upload_to='shops/products/pictures',
        blank=True, null=True,
    )

    class Meta:
        get_latest_by = ['-updated_at', ]
        order_with_respect_to = 'product'

    def __str__(self):
        return '{} product pic #{}'.format(self.product, self.pk)


class Inventory(Base):
    """
    Models the product inventory data
    """
    product = models.ForeignKey(
        Product,
        related_name='inventory',
        on_delete=models.CASCADE
    )
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    stock = models.PositiveIntegerField('Available in stock')

    class Meta:
        order_with_respect_to = 'product'

    def __str__(self):
        return 'Inventory for {}'.format(self.product)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:inventory-detail', args=[str(self.pk)])


class DeliveryMethod(Base):
    """
    Models a product delivery method type
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        get_latest_by = ['updated_at', ]

    def __str__(self):
        return self.name


class PaymentMethod(Base):
    """
    Models a payment method type
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        get_latest_by = ['updated_at', ]

    def __str__(self):
        return self.name


class Order(Base):
    cutomer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.SET(get_deleted_user)
    )
    delivery_method = models.ForeignKey(
        DeliveryMethod,
        related_name='orders',
        null=True, on_delete=models.SET_NULL,
    )
    order_date = models.DateTimeField()
    is_delivered = models.BooleanField('Delivery status', default=False)

    class Meta:
        get_latest_by = ['-order_date', ]
        ordering = ['-order_date', 'is_delivered', ]

    def __str__(self):
        return 'Order No. {}'.format(self.pk)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:order-detail', args=[str(self.pk)])


class OrderList(Base):
    """
    Models the an ordered product with respect to an Order object
    """
    order = models.ForeignKey(
        Order,
        related_name='ordered_lists',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='ordered_lists',
        null=True, on_delete=models.SET_NULL
    )
    qty = models.PositiveIntegerField('Quantity', default=1)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        order_with_respect_to = 'order'
        get_latest_by = ['-updated_at', ]

    def __str__(self):
        return '{} of {}'.format(self.product, self.order)


class Payment(Base):
    """
    Models a payment made for an order
    """
    order = models.ForeignKey(
        Order,
        related_name='payments',
        null=True, on_delete=models.SET_NULL,
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        related_name='payments',
        null=True, on_delete=models.SET_NULL
    )
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_amount = models.DecimalField(max_digits=6, decimal_places=2)
    tax = models.DecimalField(max_digits=6, decimal_places=2)
    payment_date = models.DateTimeField()
    is_payment_completed = models.BooleanField(default=False)

    class Meta:
        get_latest_by = ['-updated_at', ]
        ordering = ['is_payment_completed', '-updated_at']

    def __str__(self):
        return 'Payment for {}'.format(self.order)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('shops:payment-detail', args=[str(self.pk)])
