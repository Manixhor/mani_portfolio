from rest_framework import serializers
from .models import PageView


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ['path', 'ip_address', 'user_agent', 'referrer', 'timestamp']
        read_only_fields = ['timestamp']


class PageViewStatsSerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    top_pages = serializers.ListField(child=serializers.DictField())
