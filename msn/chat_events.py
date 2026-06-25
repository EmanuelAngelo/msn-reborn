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


def _notify_user(user_id, event_type, **payload):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {'type': event_type, **payload},
    )


def notify_message_recipients(message):
    from .models import ConversationParticipant

    payload = message_to_ws_payload(message)
    recipient_ids = (
        ConversationParticipant.objects
        .filter(conversation_id=message.conversation_id)
        .exclude(user_id=message.sender_id)
        .values_list('user_id', flat=True)
    )

    for user_id in recipient_ids:
        _notify_user(user_id, 'message.received', message=payload)


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
    notify_message_recipients(message)


def broadcast_typing(conversation_id, user, is_typing):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    profile = getattr(user, 'profile', None)
    user_payload = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'display_name': (profile.display_name if profile else None) or user.username,
    }

    async_to_sync(channel_layer.group_send)(
        f'conversation_{conversation_id}',
        {
            'type': 'chat.typing',
            'user': user_payload,
            'is_typing': is_typing,
        },
    )

    from .models import ConversationParticipant

    recipient_ids = (
        ConversationParticipant.objects
        .filter(conversation_id=conversation_id)
        .exclude(user_id=user.id)
        .values_list('user_id', flat=True)
    )

    for user_id in recipient_ids:
        _notify_user(
            user_id,
            'typing.updated',
            conversation_id=str(conversation_id),
            user=user_payload,
            is_typing=is_typing,
        )
