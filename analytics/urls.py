"""
Analytics App URLs
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('bookings/', views.booking_analytics, name='booking_analytics'),
    path('users/', views.user_analytics, name='user_analytics'),
    path('financial/', views.financial_analytics, name='financial_analytics'),
    path('performance/', views.performance_metrics, name='performance_metrics'),
    path('export/', views.export_analytics, name='export_analytics'),
    path('refresh-cache/', views.refresh_analytics_cache, name='refresh_analytics_cache'),
]
