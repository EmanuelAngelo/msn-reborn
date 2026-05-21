import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    class Status(models.TextChoices):
        ONLINE = 'online', 'Online'
        AWAY = 'away', 'Ausente'
        BUSY = 'busy', 'Ocupado'
        INVISIBLE = 'invisible', 'Invisível'
        OFFLINE = 'offline', 'Offline'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=80)
    personal_message = models.CharField(max_length=180, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceita'
        REJECTED = 'rejected', 'Recusada'
        CANCELED = 'canceled', 'Cancelada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_contact_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_contact_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_contact_request_sender_receiver')]

    def __str__(self):
        return f'{self.sender} -> {self.receiver}'


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_of')
    nickname = models.CharField(max_length=80, blank=True)
    is_blocked = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'contact'], name='unique_owner_contact')]

    def __str__(self):
        return f'{self.owner} adicionou {self.contact}'


class Conversation(models.Model):
    class Type(models.TextChoices):
        DIRECT = 'direct', 'Individual'
        GROUP = 'group', 'Grupo'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.DIRECT)
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or str(self.id)


class ConversationParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversation_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(blank=True, null=True)
    is_muted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['conversation', 'user'], name='unique_conversation_participant')]

    def __str__(self):
        return f'{self.user} em {self.conversation}'


class Message(models.Model):
    class Type(models.TextChoices):
        TEXT = 'text', 'Texto'
        SYSTEM = 'system', 'Sistema'
        NUDGE = 'nudge', 'Chamar atenção'
        MUSIC = 'music', 'Música'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TEXT)
    content = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender', 'sent_at']),
        ]

    def __str__(self):
        return f'{self.sender}: {self.content[:30]}'


class PresenceSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='presence_sessions')
    channel_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(blank=True, null=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {"online" if self.is_active else "offline"}'


class SpotifyIntegration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spotify_integration')
    spotify_user_id = models.CharField(max_length=120, blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Spotify de {self.user}'


class UserMusicPreference(models.Model):
    class Visibility(models.TextChoices):
        CONTACTS = 'contacts', 'Somente contatos'
        PRIVATE = 'private', 'Privado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='music_preference')
    enabled = models.BooleanField(default=False)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.CONTACTS)
    show_album_cover = models.BooleanField(default=False)
    show_when_paused = models.BooleanField(default=False)
    show_spotify_link = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Preferência musical de {self.user}'


class UserMusicStatus(models.Model):
    class Provider(models.TextChoices):
        SPOTIFY = 'spotify', 'Spotify'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='music_status')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.SPOTIFY)
    track_name = models.CharField(max_length=255, blank=True)
    artist_name = models.CharField(max_length=255, blank=True)
    album_name = models.CharField(max_length=255, blank=True)
    album_cover_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)
    spotify_track_id = models.CharField(max_length=120, blank=True)
    is_playing = models.BooleanField(default=False)
    progress_ms = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    last_played_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.track_name:
            return f'{self.artist_name} - {self.track_name}'
        return f'Sem música - {self.user}'
