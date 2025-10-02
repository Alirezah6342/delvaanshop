from urllib import request
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django.views.generic import TemplateView

from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, UpdateCartItemSerializer

from store.models import Cart, CartItem

class CartPageview(TemplateView):
    template_name = 'cart.html'
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    
    def get_queryset(self): # type: ignore
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()   
    
    def get_serializer_class(self): # type: ignore
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}
    
class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()
    lookup_value_regex = ('[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}') # type: ignore
    

    
