from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('company/<slug:slug>/', views.company_detail, name='company_detail'),
    path('perfume/<int:pk>/', views.perfume_detail, name='perfume_detail'),
]
