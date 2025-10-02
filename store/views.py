from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.db.models import Q


from .forms import ProductForm, CommentForm
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
        return super().get_queryset().prefetch_related('products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.object.get_descendants(include_self=True) # type: ignore
        products = Product.objects.filter(category__in=categories).select_related('category')
        context['products'] = products
        context["descendants"] = self.object.get_descendants(include_self=False).select_related("parent")  # type: ignore
        return context


class ProductListView(generic.ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 3
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')
    


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'
    paginate_by = 2
    
    
    def get_queryset(self):
        return Product.objects.select_related('category')
    
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
        
        return super().form_valid(form)
    
    
    
class ProductSearchView(generic.ListView):
    model = Product
    template_name = "store/search_results.html"
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset =  queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(short_description__icontains=search_query)
            )
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(unit_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(unit_price__lte=max_price)
            
        return queryset
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get("q", "").strip()
        context['current_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['no_results'] = not self.get_queryset().exists()
        return context
