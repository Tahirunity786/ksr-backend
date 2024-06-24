import json
import logging
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from core_messaging.models import ChatThread, Chatmessage
from core_messaging.serializers import ChatMessageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        second_user = self.scope['target']
        first_user = self.scope['user']
        thread = await self.get_thread(first_user, second_user)
        self.chatroom = f'chatroom_{thread.id}'
        self.thread = thread

        await self.channel_layer.group_add(
            self.chatroom,
            self.channel_name
        )
        await self.send({"type": "websocket.accept"})

        # Fetch chat history
        chat_history = await self.fetch_chat_history(thread)
        await self.send({
            "type": "websocket.send",
            "text": json.dumps({
                "type": "chat_history",
                "messages": chat_history
            })
        })

    async def websocket_receive(self, event):
        try:
            message_data = json.loads(event['text'])
            logger.info(f"Received message data: {message_data}")

            message = message_data.get('message')
            if not message:
                raise ValueError("No message content")

            if not self.scope['user'] or not self.scope['target'] or not self.thread:
                raise ValueError("Invalid user, target, or thread")

            # Ensure user and thread are valid
            user = await self.get_user(self.scope['user'].id)
            thread = await self.get_thread(self.scope['user'], self.scope['target'])
            if not user or not thread:
                raise ValueError("User or thread not found")

            # Add sender to receiver's messaging container and vice versa
            await self.add_to_messaging_container(self.scope['user'], self.scope['target'])

            msg = await self.save_message(thread, user, message)
            data = ChatMessageSerializer(msg, many=False).data

            response = {
                'message': json.dumps(data),
            }

            await self.channel_layer.group_send(
                self.chatroom,
                {
                    'type': 'chat_message',
                    'text': json.dumps(response)
                }
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            await self.send({
                "type": "websocket.send",
                "text": json.dumps({'error': 'Invalid JSON data received'})
            })
        except ValueError as e:
            logger.error(f"ValueError: {e}")
            await self.send({
                "type": "websocket.send",
                "text": json.dumps({'error': str(e)})
            })
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await self.send({
                "type": "websocket.send",
                "text": json.dumps({'error': 'Internal server error'})
            })

    async def chat_message(self, event):
        await self.send({'type': 'websocket.send', 'text': event['text']})

    async def websocket_disconnect(self, event):
        await self.check_messages_count(self.thread)
        await self.channel_layer.group_discard(
            self.chatroom,
            self.channel_name
        )

    @database_sync_to_async
    def get_user(self, user_id):
        usr = User.objects.filter(id=user_id)
        if usr.exists():
            return usr.first()
        return None

    @database_sync_to_async
    def check_messages_count(self, thread):
        if thread.chatmessage_thread.all().count() == 0:
            thread.delete()

    @database_sync_to_async
    def get_thread(self, first_person, second_person):
        thread = ChatThread.objects.filter(
            Q(primary_user=first_person, secondary_user=second_person) |
            Q(primary_user=second_person, secondary_user=first_person)
        ).first()

        if thread:
            return thread
        return ChatThread.objects.create(primary_user=first_person, secondary_user=second_person)

    @database_sync_to_async
    def save_message(self, thread, user, message):
        return Chatmessage.objects.create(thread=thread, user=user, message=message)

    @database_sync_to_async
    def fetch_chat_history(self, thread):
        messages = Chatmessage.objects.filter(thread=thread).order_by('message_time')
        return ChatMessageSerializer(messages, many=True).data

    @database_sync_to_async
    def add_to_messaging_container(self, sender, receiver):
        receiver_obj = User.objects.get(id=receiver.id)
        sender_obj = User.objects.get(id=sender.id)
        receiver_obj.users_messaging_container.add(sender_obj)
        sender_obj.users_messaging_container.add(receiver_obj)
