from tokenize import Comment
from rest_framework import serializers
from django.utils.text import slugify


from store.models import Cart, CartItem, Order, OrderItem, Product, Category, Customer, Address



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'slug', 'unit_price', 'description', 'short_description', 'inventory', 'discounts', 'is_active', ]
    
    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product
           
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number', 'birth_date', ]
        read_only_fields = ['user', ]
        
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'top_product', ]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body', ]
        
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', ]
    
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'unit_price', ]
        
        
class CartProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price', ]
        
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']    
        
            
class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', ]
        
    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product.id)
            cart_item.quantity += quantity 
            cart_item.save() 
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)
            
        self.instance = cart_item
        return cart_item

        
class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializers()
    item_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id','product', 'quantity', 'item_total', ]
    
    def get_item_total(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', ]
        read_only_fields = ['id', ]
        
    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    