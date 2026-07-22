from django.urls import path
from .views import PortfolioConfigView, PortfolioConfigUpdateView

urlpatterns = [
    path('config/', PortfolioConfigView.as_view(), name='portfolio-config'),
    path('config/update/', PortfolioConfigUpdateView.as_view(), name='portfolio-config-update'),
]
