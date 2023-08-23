from FashionPlace.models import *


def category_links(request):
    category = Category.objects.all()
    return {'categories': category}