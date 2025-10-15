from store.models import Product

for product in Product.objects.all():
    if product.category:
        product.categories.add(product.category)
        print(f"✅ انتقال انجام شد برای {product.name}")
