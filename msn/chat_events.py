from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Message


def message_to_ws_payload(message):
    sender = message.sender
    return {
        'id': str(message.id),
        'conversation': str(message.conversation_id),
        'sender': str(message.sender_id),
        'sender_name': sender.profile.display_name or sender.username,
        'sender_obj': {
            'id': str(sender.id),
            'username': sender.username,
            'email': sender.email,
        },
        'type': message.type,
        'content': message.content,
        'is_read': message.is_read,
        'sent_at': message.sent_at.isoformat(),
    }


def broadcast_chat_message(message):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload = message_to_ws_payload(message)
    group_name = f'conversation_{message.conversation_id}'

    if message.type == Message.Type.NUDGE:
        event = {'type': 'chat.nudge', 'message': payload}
    else:
        event = {'type': 'chat.message', 'message': payload}

    async_to_sync(channel_layer.group_send)(group_name, event)


def broadcast_typing(conversation_id, user, is_typing):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        f'conversation_{conversation_id}',
        {
            'type': 'chat.typing',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'display_name': user.profile.display_name or user.username,
            },
            'is_typing': is_typing,
        },
    )
