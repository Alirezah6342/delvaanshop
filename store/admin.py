from django.contrib import admin
from mptt.admin import MPTTModelAdmin
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
    list_display = ['id', 'title', 'parent', 'short_description', 'top_product', 'slug']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title', )}
    list_select_related = ['top_product', 'parent']
    list_filter = ['parent']
    list_per_page = 10
    
    @admin.display(description='Description')
    def short_description(self, obj):
        return obj.description[:30]
    

    
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
