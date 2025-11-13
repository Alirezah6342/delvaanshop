from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField
# from django.utils.text import slugify

from uuid import uuid4

from core.models.mixins import GenerateSlugMixin

class Category(GenerateSlugMixin, MPTTModel):
    slug_field_name = 'slug'
    source_field_name = 'title'
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', db_index=True)
    top_product = models.ForeignKey('Product', on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    
    class MPTTMeta:
        order_insertion_by = ['title']
    
    class Meta: # type: ignore
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ('parent', 'slug')

    # def __str__(self):
    # نمایش مسیر کامل برای دسته‌بندی‌ها (مثلاً "زنانه > لباس > پیراهن")
        # ancestors = self.get_ancestors(include_self=True)
        # return " > ".join([a.title for a in ancestors])

    def __str__(self) -> str:
        return self.title
    
    def get_full_path(self):
        return ">".join(a.title for a in self.get_ancestors(include_self=True))
    
    
    def get_absolute_url(self):
        return reverse("category_detail", kwargs={'pk': self.pk, 'slug': self.slug})
    

class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return f'{str(self.discount)} | {self.description}'    


class Product(GenerateSlugMixin, models.Model):
    slug_field_name = 'slug'
    source_field_name = 'name'
    
    name = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    unit_price = models.PositiveIntegerField(default=0)
    description = RichTextField()
    short_description = models.TextField()
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    discounts = models.ManyToManyField(Discount, blank=True)
    is_active = models.BooleanField(default=True)
    cover = models.ImageField(upload_to='store/covers/', blank=True)
    
    
    def __str__(self) -> str:
        return self.name
    
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={'pk': self.pk, 'slug': self.slug})
    
    
    @property
    def approved_comments(self):
        return list(self.comments.filter(status='a').select_related('user')) # type: ignore
    

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
   
    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.username
         
    
    def __str__(self):
        return self.full_name
    
class Address(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    full_address = models.TextField()
    
    
class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    
    ORDER_STATUS = [
        (ORDER_STATUS_PAID, 'Paid'),
        (ORDER_STATUS_UNPAID, 'Unpaid'),
        (ORDER_STATUS_CANCELED, 'Canceled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default=ORDER_STATUS_UNPAID)
    order_notes = models.CharField(max_length=700, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        customer_name = self.customer.full_name if self.customer else "Unknown Customer"
        return f"Order #{self.pk} - {customer_name}"

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.PositiveIntegerField()
    
    def __str__(self):
        return f'OrderItem {self.pk}: {self.product} × {self.quantity} (unit_price: {self.unit_price})'
    
    class Meta:
        unique_together = [['order', 'product']]
        
        
        
class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED ='na'
    
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    body = models.TextField(verbose_name=_('Comment Text'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING)
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={'pk': self.product.pk, 'slug': self.product.slug})
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['status'])
        ]
        
    def __str__(self):
        return self.name
    
        
    
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField()
    
    class Meta:
        unique_together = [['cart', 'product']]
          