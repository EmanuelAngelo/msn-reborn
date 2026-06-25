from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Contact, ContactRequest, Conversation, Message, UserMusicPreference, UserMusicStatus, UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'display_name']
        read_only_fields = ['id']

    def create(self, validated_data):
        display_name = validated_data.pop('display_name', '')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if display_name:
            user.profile.display_name = display_name
            user.profile.save(update_fields=['display_name', 'updated_at'])
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id', 'email', 'username', 'display_name',
            'personal_message', 'avatar', 'avatar_url', 'status', 'last_seen_at'
        ]
        read_only_fields = ['id', 'user_id', 'email', 'username', 'avatar_url', 'last_seen_at']

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return ''
        return obj.avatar.url


class UserSearchSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']


class MusicStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMusicStatus
        fields = [
            'provider', 'track_name', 'artist_name', 'album_name', 'album_cover_url',
            'spotify_url', 'spotify_track_id', 'is_playing', 'progress_ms', 'duration_ms', 'updated_at'
        ]


class MusicPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMusicPreference
        fields = ['enabled', 'visibility', 'show_album_cover', 'show_when_paused', 'show_spotify_link']


class ContactSerializer(serializers.ModelSerializer):
    contact_profile = serializers.SerializerMethodField()
    music_status = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'contact', 'contact_profile', 'music_status',
            'nickname', 'is_blocked', 'is_favorite', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_contact_profile(self, obj):
        profile = obj.contact.profile
        data = UserProfileSerializer(profile, context=self.context).data
        request = self.context.get('request')

        if (
            profile.status == UserProfile.Status.INVISIBLE
            and request
            and request.user != obj.contact
        ):
            data = {**data, 'status': UserProfile.Status.OFFLINE}

        return data

    def get_music_status(self, obj):
        pref = getattr(obj.contact, 'music_preference', None)
        status = getattr(obj.contact, 'music_status', None)

        if not pref or not status:
            return None

        if not pref.enabled:
            return None

        if pref.visibility == UserMusicPreference.Visibility.PRIVATE:
            request = self.context.get('request')
            if not request or request.user != obj.contact:
                return None

        if not pref.show_when_paused and not status.is_playing:
            return None

        data = MusicStatusSerializer(status).data

        if not pref.show_album_cover:
            data['album_cover_url'] = ''

        if not pref.show_spotify_link:
            data['spotify_url'] = ''

        return data


class ContactRequestSerializer(serializers.ModelSerializer):
    sender_profile = UserProfileSerializer(source='sender.profile', read_only=True)
    receiver_profile = UserProfileSerializer(source='receiver.profile', read_only=True)

    class Meta:
        model = ContactRequest
        fields = [
            'id', 'sender', 'receiver', 'sender_profile', 'receiver_profile',
            'status', 'message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sender', 'status', 'created_at', 'updated_at']

    def validate_receiver(self, receiver):
        request = self.context.get('request')
        if request and receiver == request.user:
            raise serializers.ValidationError('Você não pode enviar solicitação para você mesmo.')
        if request and Contact.objects.filter(owner=request.user, contact=receiver, is_blocked=False).exists():
            raise serializers.ValidationError('Esse usuário já está na sua lista de contatos.')
        if request and ContactRequest.objects.filter(sender=request.user, receiver=receiver, status=ContactRequest.Status.PENDING).exists():
            raise serializers.ValidationError('Você já enviou uma solicitação pendente para esse usuário.')
        return receiver


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.profile.display_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'type', 'content', 'is_read', 'sent_at']
        read_only_fields = ['conversation', 'sender', 'is_read', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants_count = serializers.IntegerField(source='participants.count', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'type', 'title', 'participants_count', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        message = obj.messages.order_by('-sent_at').first()
        return MessageSerializer(message).data if message else None
