from django.urls import path
from core_messaging.views import ReceivedMessagesView
urlpatterns = [
    path('recievers-list/', ReceivedMessagesView.as_view())
]
