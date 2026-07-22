from rest_framework import generics, permissions
from .models import PortfolioConfig
from .serializers import PortfolioConfigSerializer


class PortfolioConfigView(generics.RetrieveAPIView):
    queryset = PortfolioConfig.objects.all()
    serializer_class = PortfolioConfigSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        obj, _ = PortfolioConfig.objects.get_or_create(pk=1)
        return obj


class PortfolioConfigUpdateView(generics.UpdateAPIView):
    queryset = PortfolioConfig.objects.all()
    serializer_class = PortfolioConfigSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        obj, _ = PortfolioConfig.objects.get_or_create(pk=1)
        return obj
