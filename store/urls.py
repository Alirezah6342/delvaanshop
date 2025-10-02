from django.urls import include, path, register_converter

from .import views
from .converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    path('', views.HomeView.as_view(), name='home_page'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/<uslug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/<uslug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.ProductSearchView.as_view(), name='search_results'),
    path('comment/<int:product_id>/', views.CommentCreateView.as_view(), name='comment_create'),
    path('api/', include('store.api.urls')),
]


# from .import views


# from rest_framework.routers import DefaultRouter
# from rest_framework_nested.routers import NestedDefaultRouter


# router = DefaultRouter()
# router.register('products', views.ProductListView.as_view(), basename='product')
# router.register('categories', views.CategoryListView.as_view(), basename='category')
# router.register('carts', views.CartViewSet, basename='cart')
# router.register('customers', views.CustomerViewSet, basename='customer')
# router.register('orders', views.OrderViewSet, basename='order')


# products_router = NestedDefaultRouter(router, 'products', lookup='product')
# products_router.register('comments', views.CommentViewSet, basename='product-comment')


# cart_items_router = NestedDefaultRouter(router, 'carts', lookup='cart')
# cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')

# urlpatterns = router.urls + products_router.urls + cart_items_router.urls
