from django_filters import rest_framework as filters
from FashionPlace.models import Product, Category

class ProductFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category',
        to_field_name='slug',
        empty_label='All Categories'
    )

    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'price': ['gt', 'lt']
        }