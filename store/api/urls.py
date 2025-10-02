from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework_nested import routers

from . import views


router = DefaultRouter()
router.register('carts', views.CartViewSet)

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewSet, basename='cart-item')



html_urlpatterns = [
    path('cart-page/', views.CartPageview.as_view(), name='cart_page'),
]


urlpatterns = router.urls + cart_items_router.urls + html_urlpatterns
