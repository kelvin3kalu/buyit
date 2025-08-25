from .models import Product
from django import forms

class Podu(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']