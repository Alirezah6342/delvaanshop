from django.contrib import admin
from mptt.admin import MPTTModelAdmin, TreeRelatedFieldListFilter
from django.db.models.query import QuerySet
from django.http import HttpRequest

from . import models


class CommentsInline(admin.TabularInline):
    model = models.Comment
    fields = ['name', 'body', 'status']
    extra = 1

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit_price', 'inventory', 'is_active', 'slug']
    list_editable = ['inventory', 'unit_price']
    list_filter = ['categories', 'is_active']
    search_fields = ['name', 'categories__title']
    prepopulated_fields = {'slug': ('name', )}
    inlines = [CommentsInline, ]
    filter_horizontal = ('categories', )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('categories')
    

@admin.register(models.Category)
class CategoryAdmin(MPTTModelAdmin):
    mptt_level_indent = 40
    list_display = ['id', 'get_full_path', 'title', 'parent', 'top_product', 'slug']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title', )}
    list_select_related = ['top_product', 'parent']
    list_filter = (('parent', TreeRelatedFieldListFilter), )
    list_per_page = 10
    
    @admin.display(description='Full Path')
    def get_full_path(self, obj):
        return obj.get_full_path
    

    
@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'name', 'short_body', 'status']
    list_filter = ['status']
    search_fields = ['name', 'product__name', 'body']
    ordering = ['-id']
    list_select_related = ['product']
    
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('product')
    
    
    @admin.display(description='Body')
    def short_body(self, obj):
        return obj.body[:30]
    

class CartItemInline(admin.TabularInline):
    model = models.CartItem
    fields = ['id', 'product', 'quantity']
    extra = 0
    min_num = 1
    
        
@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ['order', 'product', 'quantity', 'unit_price',]
    extra = 0
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_full_name', 'datetime_created', 'status', ]
    search_fields = ['customer__user__first_name', 'customer__user__last_name']
    list_select_related = ['customer', 'customer__user']
    inlines = [OrderItemInline, ]
    
        
    @admin.display(description='Customer Full Name', ordering='customer__user__first_name')
    def customer_full_name(self, obj):
        return obj.customer.full_name
    

@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', ]
    
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'birth_date', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone_number']
    list_select_related = ['user']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
