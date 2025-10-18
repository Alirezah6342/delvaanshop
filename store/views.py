from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.db.models import Q

from .cart import Cart
from .forms import ProductForm, CommentForm, AddToCartProductForm
from .models import Category, Customer, Product, Comment


class HomeView(generic.TemplateView):
    template_name = 'store/home_page.html'


class CategoryListView(generic.ListView):
    model = Category
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.root_nodes().prefetch_related('children') # type: ignore


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    source_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('products', 'children')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.object.get_descendants(include_self=True) # type: ignore
        products = Product.objects.filter(categories__in=categories).prefetch_related('categories')
        context['products'] = products.distinct()
        context["descendants"] = self.object.get_descendants(include_self=False).prefetch_related("parent")  # type: ignore
        return context


class ProductListView(generic.ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 4
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('categories')
    


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'
    paginate_by = 2
    
    
    def get_queryset(self):
        return Product.objects.prefetch_related('categories').prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('user').order_by('-datetime_created')
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context
    
class CommentCreateView(generic.CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        
        product_id = int(self.kwargs['product_id'])
        product = get_object_or_404(Product, id=product_id)
        obj.product = product
        
        messages.success(self.request, _('Comment successfully created'))
        
        return super().form_valid(form)
    
    
    
class ProductSearchView(generic.ListView):
    model = Product
    template_name = "store/search_results.html"
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).prefetch_related(
            Prefetch(
            'categories', 
            queryset=Category.objects.all().prefetch_related('parent')
            )
        ) 
        
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset =  queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(short_description__icontains=search_query)
            )
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
            
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(unit_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(unit_price__lte=max_price)
            
        return queryset.distinct()
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        products = context['products']
        
        product_ids = [product.id for product in products]
        product_ids = [p.id for p in products]
        category_ids = (Category.objects.filter(products__id__in=product_ids).values_list("id", flat=True).distinct())
        categories = Category.objects.filter(id__in=list(category_ids))
        # categories = Category.objects.filter(products__in=products).distinct()
        # if not hasattr(self, '_all_categories'):
        #     self._all_categories = Category.objects.all()
        context['categories'] = categories
        context['search_query'] = self.request.GET.get("q", "").strip()
        context['current_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['no_results'] = not context['products'].exists()
        return context


def cart_detail_view(request):
    cart = Cart(request)
    for item in cart:
        item['product_update_quantity_form'] = AddToCartProductForm(initial={
            'quantity': item['quantity'],
            'inplace': True,
            })
    
    return render(request, 'cart_detail.html', {'cart': cart, })
 
 
@require_POST    
def add_to_cart_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartProductForm(request.POST)
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        cart.add(product, quantity, replace_current_quantity=cleaned_data['inplace'])
        
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart.remove(product)
    
    return redirect('cart_detail')
