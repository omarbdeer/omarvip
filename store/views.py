from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    all_products = category.products.prefetch_related('images').all()
    paginator = Paginator(all_products, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'store/category.html', {
        'category': category,
        'products': page,
        'page_obj': page,
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
