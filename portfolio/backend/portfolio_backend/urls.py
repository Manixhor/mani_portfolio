from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

admin.site.site_header = 'Manikanta Portfolio Admin'
admin.site.site_title = 'Portfolio Admin'
admin.site.index_title = 'Dashboard'


def health_view(_request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('healthz/', health_view, name='healthz'),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/portfolio/', include('portfolio_data.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
