from django.shortcuts import render, get_object_or_404
from django.conf import settings

from .models import Company, Perfume


def home(request):
    companies = Company.objects.all()
    return render(request, 'store/home.html', {'companies': companies})


def company_detail(request, slug):
    company = get_object_or_404(Company, slug=slug)
    perfumes = company.perfumes.prefetch_related('sizes').all()
    return render(request, 'store/company.html', {
        'company': company,
        'perfumes': perfumes,
    })


def perfume_detail(request, pk):
    perfume = get_object_or_404(
        Perfume.objects.select_related('company').prefetch_related('sizes'),
        pk=pk,
    )
    perfume_url = request.build_absolute_uri()
    whatsapp_msg = (
        f'Hi, I want to order: {perfume.company.name} — {perfume.name}\n'
        f'Link: {perfume_url}'
    )
    whatsapp_url = f'https://wa.me/{settings.WHATSAPP_NUMBER}?text={whatsapp_msg}'
    return render(request, 'store/perfume.html', {
        'perfume': perfume,
        'whatsapp_url': whatsapp_url,
    })
