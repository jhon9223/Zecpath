from django.urls import path
from . import views

urlpatterns = [
    path(
        "conversations/",
        views.ConversationListAPIView.as_view(),
        name="chat-conversations",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        views.MessageListCreateAPIView.as_view(),
        name="chat-messages",
    ),
    path(
        "applications/<int:application_id>/start/",
        views.StartConversationAPIView.as_view(),
        name="chat-start",
    ),
]
