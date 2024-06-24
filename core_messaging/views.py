from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .models import ChatThread, Chatmessage
User = get_user_model()


class ReceivedMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        # Find all threads where the user is the primary user or secondary user
        primary_threads = ChatThread.objects.filter(primary_user_id=user_id)
        secondary_threads = ChatThread.objects.filter(secondary_user_id=user_id)

        # Get all messages where the user is the sender
        sent_messages = Chatmessage.objects.filter(
            thread__in=primary_threads, user_id=user_id
        ).values_list('thread__secondary_user', flat=True).distinct()

        # Get all messages where the user is the receiver
        received_messages = Chatmessage.objects.filter(
            thread__in=secondary_threads
        ).exclude(user_id=user_id).values_list('user', flat=True).distinct()

        # Fetch the sender and receiver user details
        senders = User.objects.filter(id__in=received_messages)
        receivers = User.objects.filter(id__in=sent_messages)

        user_data = []

        for sender in senders:
            user_data.append({
                "id": sender.id,
                "firstname": sender.first_name,
                "lastname": sender.last_name,
                "profile": sender.profile if sender.profile else None,
                "role": "sender"
            })

        for receiver in receivers:
            user_data.append({
                "id": receiver.id,
                "firstname": receiver.first_name,
                "lastname": receiver.last_name,
                "profile": receiver.profile if receiver.profile else None,
                "role": "receiver"
            })

        return Response(user_data, status=status.HTTP_200_OK)
