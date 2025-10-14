from django import forms

from .models import Product, Comment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'categories', 'unit_price', 'description', 'short_description', 'inventory', 'discounts', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name'}),
            'unit_price': forms.NumberInput(attrs={'min': 0}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']



class AddToCartProductForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 31)]
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
    
    inplace = forms.BooleanField(required=False, widget=forms.HiddenInput)
    