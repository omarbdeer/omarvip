import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

ALKHAIR_URL = os.environ.get('ALKHAIR_URL', 'https://alkhair-xxxx.run.app')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alkhair-payment', RedirectView.as_view(url=ALKHAIR_URL, permanent=False)),
    path('alkhair-payment/', RedirectView.as_view(url=ALKHAIR_URL, permanent=False)),
    path('', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
