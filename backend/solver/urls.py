from django.urls import path
from .views import (SolveView, HistoryListView, StatsView, ClassifyView,
                    ConversationListView, MessageListView, ReferenceView, ConversationExportView)

urlpatterns = [
    path('problems/<int:pk>/reference/', ReferenceView.as_view(), name='reference'),
    path('conversations/<int:pk>/export/', ConversationExportView.as_view(), name='conversation-export'),
    path('classify/', ClassifyView.as_view(), name='classify'),
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:pk>/messages/', MessageListView.as_view(), name='messages'),
    path('solve/',   SolveView.as_view(),       name='solve'),
    path('history/', HistoryListView.as_view(),  name='history'),
    path('stats/',   StatsView.as_view(),        name='stats'),
]
