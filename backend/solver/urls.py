from django.urls import path
from .views import SolveView, HistoryListView, StatsView

urlpatterns = [
    path('solve/',   SolveView.as_view(),       name='solve'),
    path('history/', HistoryListView.as_view(),  name='history'),
    path('stats/',   StatsView.as_view(),        name='stats'),
]
