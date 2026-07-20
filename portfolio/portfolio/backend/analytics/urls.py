from django.urls import path
from .views import PageViewCreateView, PageViewStatsView

urlpatterns = [
    path('track/', PageViewCreateView.as_view(), name='analytics-track'),
    path('stats/', PageViewStatsView.as_view(), name='analytics-stats'),
]
