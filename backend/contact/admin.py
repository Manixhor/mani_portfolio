from django.contrib import admin
from django import forms
from django.utils.html import format_html
from tinymce.widgets import TinyMCE
from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 15}))

    class Meta:
        model = ContactMessage
        fields = '__all__'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    form = ContactMessageForm
    list_display = ['name', 'email', 'subject', 'status_badge', 'created_at']
    list_editable = []
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'message_preview']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']
    fieldsets = [
        ('Sender', {'fields': ['name', 'email']}),
        ('Message', {'fields': ['subject', 'message', 'message_preview', 'is_read']}),
        ('Metadata', {'fields': ['created_at']}),
    ]

    @admin.display(description='Status')
    def status_badge(self, obj):
        label = 'Read' if obj.is_read else 'Unread'
        class_name = 'admin-badge read' if obj.is_read else 'admin-badge unread'
        return format_html('<span class="{}">{}</span>', class_name, label)

    @admin.display(description='Message Preview')
    def message_preview(self, obj):
        return format_html('<div class="admin-preview">{}</div>', obj.message)

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}
