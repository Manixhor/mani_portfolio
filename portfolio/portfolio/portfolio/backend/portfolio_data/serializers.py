from rest_framework import serializers
from .models import PortfolioConfig


class PortfolioConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioConfig
        fields = ['hero', 'about', 'experience', 'skills', 'projects', 'contact', 'footer', 'updated_at']
