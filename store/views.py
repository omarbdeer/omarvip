from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.prefetch_related('images').all()
    return render(request, 'store/category.html', {
        'category': category,
        'products': products,
        'whatsapp': settings.WHATSAPP_NUMBER,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_url = request.build_absolute_uri()
    whatsapp_msg = f'Hi Omar, I want to order: {product.name}\nProduct link: {product_url}'
    whatsapp_url = f'https://wa.me/{settings.WHATSAPP_NUMBER}?text={whatsapp_msg}'
    return render(request, 'store/product.html', {
        'product': product,
        'whatsapp_url': whatsapp_url,
    })
