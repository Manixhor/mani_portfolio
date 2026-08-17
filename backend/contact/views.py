import json
import logging
import urllib.request
import urllib.error

from django.conf import settings
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from portfolio_data.models import PortfolioConfig


logger = logging.getLogger(__name__)

GMAIL_RELAY_URL = getattr(settings, 'GMAIL_RELAY_URL', '')


def get_notification_recipients():
    config = PortfolioConfig.objects.filter(pk=1).first()
    if config and config.notification_emails:
        return [
            email.strip()
            for email in config.notification_emails.split(',')
            if email.strip()
        ]

    configured_email = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', '')
    if configured_email:
        return [configured_email]

    contact_email = ((config.contact or {}).get('email') if config else '') or ''
    if contact_email:
        return [contact_email]

    return []


def send_via_relay(subject, body, to_email):
    if not GMAIL_RELAY_URL:
        return False
    try:
        payload = json.dumps({
            'to': to_email,
            'subject': subject,
            'body': body,
            'from': 'manigururam08@gmail.com',
            'name': 'Portfolio',
        }).encode('utf-8')
        req = urllib.request.Request(
            GMAIL_RELAY_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
        with opener.open(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get('success', False)
    except urllib.error.HTTPError as e:
        logger.exception("Gmail relay HTTP %s.", e.code)
        return False
    except Exception:
        logger.exception("Gmail relay failed.")
        return False


@method_decorator(csrf_exempt, name='dispatch')
class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'contact'

    def perform_create(self, serializer):
        serializer.save()


class ContactListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
