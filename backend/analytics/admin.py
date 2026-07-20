from django.contrib import admin
from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['path', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['path', 'ip_address']
    readonly_fields = ['path', 'ip_address', 'user_agent', 'referrer', 'timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}
