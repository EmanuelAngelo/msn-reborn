from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .models import Conversation, ConversationParticipant, Message, UserProfile


def extract_token(query_string: bytes):
    query = query_string.decode()
    for part in query.split('&'):
        if part.startswith('token='):
            return part.replace('token=', '', 1).strip()
    return ''


class PresenceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        token_key = extract_token(self.scope.get('query_string', b''))
        self.user = await self.get_user_by_token(token_key)

        if not self.user:
            await self.close(code=4001)
            return

        self.global_group = 'presence_global'
        self.user_group = f'user_{self.user.id}'

        await self.channel_layer.group_add(self.global_group, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
        await self.set_user_status('online')
        await self.channel_layer.group_send(
            self.global_group,
            {
                'type': 'presence.status',
                'user_id': str(self.user.id),
                'status': 'online',
            },
        )

        await self.send_json({'type': 'presence.connected', 'user_id': str(self.user.id)})

    async def disconnect(self, close_code):
        if hasattr(self, 'global_group'):
            await self.set_user_status('offline')
            await self.channel_layer.group_send(
                self.global_group,
                {
                    'type': 'presence.status',
                    'user_id': str(self.user.id),
                    'status': 'offline',
                },
            )
            await self.channel_layer.group_discard(self.global_group, self.channel_name)
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('type') == 'presence.ping':
            await self.send_json({'type': 'presence.pong'})

    async def presence_status(self, event):
        await self.send_json(
            {
                'type': 'contact_status_updated',
                'user_id': event['user_id'],
                'status': event['status'],
            }
        )

    async def contact_request_created(self, event):
        await self.send_json(
            {
                'type': 'contact_request_created',
                'request': event.get('request'),
            }
        )

    async def contact_request_updated(self, event):
        await self.send_json(
            {
                'type': 'contact_request_updated',
                'request': event.get('request'),
            }
        )

    async def contacts_changed(self, event):
        await self.send_json(
            {
                'type': 'contacts_changed',
                'reason': event.get('reason', ''),
            }
        )

    async def music_status_updated(self, event):
        await self.send_json(
            {
                'type': 'music_status_updated',
                'user_id': event.get('user_id'),
                'music': event.get('music'),
            }
        )

    @database_sync_to_async
    def get_user_by_token(self, token_key):
        if not token_key:
            return None
        try:
            return Token.objects.select_related('user').get(key=token_key).user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def set_user_status(self, status):
        profile = self.user.profile
        profile.status = status
        if status == UserProfile.Status.OFFLINE:
            profile.last_seen_at = timezone.now()
        profile.save(update_fields=['status', 'last_seen_at', 'updated_at'])


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'conversation_{self.conversation_id}'

        token_key = extract_token(self.scope.get('query_string', b''))
        self.user = await self.get_user_by_token(token_key)

        if not self.user:
            await self.close(code=4001)
            return

        can_access = await self.user_can_access_conversation(
            user_id=str(self.user.id),
            conversation_id=self.conversation_id,
        )

        if not can_access:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(
            {
                'type': 'connection.accepted',
                'conversation_id': self.conversation_id,
                'message': 'Conectado ao chat em tempo real.',
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event_type = content.get('type')

        if event_type == 'message.send':
            await self.handle_message_send(content)
        elif event_type == 'typing.start':
            await self.broadcast_typing(is_typing=True)
        elif event_type == 'typing.stop':
            await self.broadcast_typing(is_typing=False)
        elif event_type == 'nudge.send':
            await self.handle_nudge_send()

    async def handle_message_send(self, content):
        text = (content.get('content') or '').strip()
        if not text:
            return

        message = await self.create_message(
            conversation_id=self.conversation_id,
            sender_id=str(self.user.id),
            content=text,
            message_type='text',
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': message,
            },
        )

    async def handle_nudge_send(self):
        message = await self.create_message(
            conversation_id=self.conversation_id,
            sender_id=str(self.user.id),
            content='Chamou sua atenção!',
            message_type='nudge',
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.nudge',
                'message': message,
            },
        )

    async def broadcast_typing(self, is_typing):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.typing',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'email': self.user.email,
                },
                'is_typing': is_typing,
            },
        )

    async def chat_message(self, event):
        await self.send_json({'type': 'message.created', 'message': event['message']})

    async def chat_nudge(self, event):
        await self.send_json({'type': 'nudge.received', 'message': event['message']})

    async def chat_typing(self, event):
        if event['user']['id'] == str(self.user.id):
            return
        await self.send_json(
            {
                'type': 'typing.updated',
                'user': event['user'],
                'is_typing': event['is_typing'],
            }
        )

    @database_sync_to_async
    def get_user_by_token(self, token_key):
        if not token_key:
            return None
        try:
            return Token.objects.select_related('user').get(key=token_key).user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def user_can_access_conversation(self, user_id, conversation_id):
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id,
            user_id=user_id,
        ).exists()

    @database_sync_to_async
    def create_message(self, conversation_id, sender_id, content, message_type):
        conversation = Conversation.objects.get(id=conversation_id)
        message = Message.objects.select_related('sender__profile').create(
            conversation=conversation,
            sender_id=sender_id,
            content=content,
            type=message_type,
        )
        conversation.save(update_fields=['updated_at'])

        return {
            'id': str(message.id),
            'conversation': str(message.conversation_id),
            'sender': str(message.sender_id),
            'sender_name': message.sender.profile.display_name or message.sender.username,
            'sender_obj': {
                'id': str(message.sender.id),
                'username': message.sender.username,
                'email': message.sender.email,
            },
            'type': message.type,
            'content': message.content,
            'is_read': message.is_read,
            'sent_at': message.sent_at.isoformat(),
        }
