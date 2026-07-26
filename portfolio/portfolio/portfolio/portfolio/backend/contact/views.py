import logging

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, permissions
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from portfolio_data.models import PortfolioConfig


logger = logging.getLogger(__name__)


def get_notification_recipients():
    configured_email = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', '')
    if configured_email:
        return [configured_email]

    config = PortfolioConfig.objects.filter(pk=1).first()
    contact_email = ((config.contact or {}).get('email') if config else '') or ''
    if contact_email:
        return [contact_email]

    return []


class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'contact'

    def perform_create(self, serializer):
        message = serializer.save()
        recipients = get_notification_recipients()
        if not recipients:
            return

        subject = f"Portfolio contact: {message.subject}"
        body = (
            f"Name: {message.name}\n"
            f"Email: {message.email}\n"
            f"Subject: {message.subject}\n\n"
            f"{message.message}\n\n"
            "This message was submitted from your portfolio contact form."
        )
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception:
            logger.exception("Contact message email notification failed.")


class ContactListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
