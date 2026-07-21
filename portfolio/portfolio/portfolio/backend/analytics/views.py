from rest_framework import generics, permissions, views
from rest_framework.response import Response
from django.db.models import Count
from .models import PageView
from .serializers import PageViewSerializer, PageViewStatsSerializer


class PageViewCreateView(generics.CreateAPIView):
    queryset = PageView.objects.all()
    serializer_class = PageViewSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'analytics'


class PageViewStatsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total = PageView.objects.count()
        unique = PageView.objects.values('ip_address').distinct().count()
        top = (
            PageView.objects.values('path')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        data = {
            'total_views': total,
            'unique_visitors': unique,
            'top_pages': list(top),
        }
        return Response(data)
