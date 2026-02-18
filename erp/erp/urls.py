from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('system.urls')),
    path('api/v1/basic/', include('basic.urls')),
    path('api/v1/purchase/', include('purchase.urls')),
    path('api/v1/sale/', include('sale.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/finance/', include('finance.urls')),
    path('api/v1/reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
