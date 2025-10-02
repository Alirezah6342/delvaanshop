# from django import template
# from store.models import Category
# from mptt.utils import get_cached_trees  # ✅ استفاده از ابزار حرفه‌ای MPTT

# register = template.Library()

# @register.inclusion_tag('store/partials/category_menu.html', takes_context=True)
# def show_category_tree(context):
#     categories = Category.objects.all().select_related('parent')  # یا order_by('tree_id', 'lft') برای اطمینان
#     tree = get_cached_trees(categories)  # ✅ این متد بچه‌ها رو کش می‌کنه، مثل آدم حرفه‌ای
#     return {
#         'categories': tree,
#         'request': context['request'],
#         'level': 0,
#     }



from django import template
from store.models import Category
from mptt.utils import get_cached_trees

register = template.Library()

@register.inclusion_tag('store/partials/category_menu.html', takes_context=True)
def show_category_tree(context):
    categories = Category.objects.all().select_related('parent').order_by('tree_id','lft')
    tree = get_cached_trees(categories)
    return {
        'categories': tree,
        'request': context['request'],
        'level': 0,
    }
