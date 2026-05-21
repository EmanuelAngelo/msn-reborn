from datetime import timedelta
from urllib.parse import urlencode
import base64
import secrets
import requests

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core import signing
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Contact, ContactRequest, Conversation, ConversationParticipant, Message, SpotifyIntegration, UserMusicStatus
from .serializers import (
    ContactRequestSerializer, ContactSerializer, ConversationSerializer, MessageSerializer,
    MusicPreferenceSerializer, MusicStatusSerializer, RegisterSerializer, UserProfileSerializer,
    UserSearchSerializer,
)

User = get_user_model()


def auth_payload(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'profile': UserProfileSerializer(user.profile).data,
    }


def user_from_token_key(token_key):
    if not token_key:
        return None
    try:
        return Token.objects.select_related('user').get(key=token_key).user
    except Token.DoesNotExist:
        return None


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def csrf(request):
    return Response({'detail': 'CSRF cookie definido.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user.profile.status = user.profile.Status.ONLINE
    user.profile.save(update_fields=['status', 'updated_at'])
    login(request, user)
    return Response(auth_payload(user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
    user.profile.status = user.profile.Status.ONLINE
    user.profile.save(update_fields=['status', 'updated_at'])
    login(request, user)
    return Response(auth_payload(user))


@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        request.user.profile.status = request.user.profile.Status.OFFLINE
        request.user.profile.last_seen_at = timezone.now()
        request.user.profile.save(update_fields=['status', 'last_seen_at', 'updated_at'])
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response({'detail': 'Logout realizado com sucesso.'})


@api_view(['GET', 'PATCH'])
def me(request):
    if request.method == 'PATCH':
        serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(UserProfileSerializer(request.user.profile).data)



@api_view(['PATCH'])
def update_my_status(request):
    new_status = request.data.get('status')
    valid_statuses = [choice[0] for choice in request.user.profile.Status.choices]
    if new_status not in valid_statuses:
        return Response({'detail': 'Status inválido.', 'valid_statuses': valid_statuses}, status=400)
    request.user.profile.status = new_status
    if new_status == request.user.profile.Status.OFFLINE:
        request.user.profile.last_seen_at = timezone.now()
    request.user.profile.save(update_fields=['status', 'last_seen_at', 'updated_at'])
    return Response(UserProfileSerializer(request.user.profile).data)


@api_view(['GET'])
def search_users(request):
    query = (request.query_params.get('q') or '').strip()
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    if query:
        users = users.filter(Q(email__icontains=query) | Q(username__icontains=query) | Q(profile__display_name__icontains=query))
    return Response(UserSearchSerializer(users[:20], many=True).data)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer

    def get_queryset(self):
        return (
            Contact.objects
            .select_related('contact__profile', 'contact__music_status')
            .filter(owner=self.request.user, is_blocked=False)
            .order_by('-is_favorite', 'contact__profile__display_name')
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ContactRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ContactRequestSerializer

    def get_queryset(self):
        return (
            ContactRequest.objects
            .select_related('sender__profile', 'receiver__profile')
            .filter(Q(receiver=self.request.user) | Q(sender=self.request.user))
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        contact_request = self.get_object()
        if contact_request.receiver != request.user:
            return Response({'detail': 'Você não pode aceitar esta solicitação.'}, status=403)
        contact_request.status = ContactRequest.Status.ACCEPTED
        contact_request.save(update_fields=['status', 'updated_at'])
        Contact.objects.get_or_create(owner=contact_request.sender, contact=contact_request.receiver)
        Contact.objects.get_or_create(owner=contact_request.receiver, contact=contact_request.sender)
        return Response(ContactRequestSerializer(contact_request, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        contact_request = self.get_object()
        if contact_request.receiver != request.user:
            return Response({'detail': 'Você não pode recusar esta solicitação.'}, status=403)
        contact_request.status = ContactRequest.Status.REJECTED
        contact_request.save(update_fields=['status', 'updated_at'])
        return Response(ContactRequestSerializer(contact_request, context={'request': request}).data)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(participants__user=self.request.user)
            .prefetch_related('participants__user__profile')
            .distinct()
            .order_by('-updated_at')
        )

    @action(detail=False, methods=['post'])
    def direct(self, request):
        contact_id = request.data.get('contact_id')
        try:
            contact_user = User.objects.get(id=contact_id)
        except User.DoesNotExist:
            return Response({'detail': 'Contato não encontrado.'}, status=404)

        if not Contact.objects.filter(owner=request.user, contact=contact_user, is_blocked=False).exists():
            return Response({'detail': 'Esse usuário ainda não está na sua lista de contatos.'}, status=400)

        existing = Conversation.objects.filter(
            type=Conversation.Type.DIRECT,
            participants__user=request.user,
        ).filter(participants__user=contact_user).first()

        if existing:
            return Response(ConversationSerializer(existing).data)

        conversation = Conversation.objects.create(type=Conversation.Type.DIRECT)
        ConversationParticipant.objects.create(conversation=conversation, user=request.user)
        ConversationParticipant.objects.create(conversation=conversation, user=contact_user)
        return Response(ConversationSerializer(conversation).data, status=201)

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == 'POST':
            serializer = MessageSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            message = serializer.save(conversation=conversation, sender=request.user)
            conversation.save(update_fields=['updated_at'])
            return Response(MessageSerializer(message).data, status=201)
        messages = conversation.messages.select_related('sender__profile').all()[:100]
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=['post'])
    def nudge(self, request, pk=None):
        conversation = self.get_object()
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            type=Message.Type.NUDGE,
            content='Chamou sua atenção!'
        )
        return Response(MessageSerializer(message).data, status=201)


@api_view(['GET', 'PATCH'])
def music_preferences(request):
    pref = request.user.music_preference
    if request.method == 'PATCH':
        serializer = MusicPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(MusicPreferenceSerializer(pref).data)


@api_view(['GET'])
def music_status(request):
    return Response(MusicStatusSerializer(request.user.music_status).data)


def broadcast_music_status(user, status_obj):
    """Notifica usuários conectados no WebSocket de presença quando a música muda."""
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload = MusicStatusSerializer(status_obj).data
    async_to_sync(channel_layer.group_send)(
        'presence_global',
        {
            'type': 'music.status.update',
            'user_id': str(user.id),
            'music': payload,
        },
    )


def clear_music_status(user):
    status_obj, _ = UserMusicStatus.objects.get_or_create(user=user)
    status_obj.track_name = ''
    status_obj.artist_name = ''
    status_obj.album_name = ''
    status_obj.album_cover_url = ''
    status_obj.spotify_url = ''
    status_obj.spotify_track_id = ''
    status_obj.is_playing = False
    status_obj.progress_ms = 0
    status_obj.duration_ms = 0
    status_obj.last_played_at = timezone.now()
    status_obj.save()
    broadcast_music_status(user, status_obj)
    return status_obj


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def spotify_connect(request):
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        return Response({'detail': 'Configure SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no .env.'}, status=400)

    user = request.user if request.user.is_authenticated else user_from_token_key(request.query_params.get('auth_token'))
    if not user:
        return Response({'detail': 'Usuário não autenticado para conectar o Spotify.'}, status=401)

    state = signing.dumps({
        'user_id': str(user.id),
        'nonce': secrets.token_urlsafe(16),
    })
    scope = 'user-read-currently-playing user-read-playback-state user-read-private'
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'scope': scope,
        'state': state,
        'show_dialog': 'true',
    }
    return redirect('https://accounts.spotify.com/authorize?' + urlencode(params))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def spotify_callback(request):
    received_state = request.GET.get('state')
    code = request.GET.get('code')

    try:
        state_payload = signing.loads(received_state, max_age=600)
        user = User.objects.get(id=state_payload.get('user_id'))
    except Exception:
        return Response({'detail': 'State inválido ou expirado. Inicie novamente pelo botão Conectar Spotify.'}, status=400)

    if not code:
        return Response({'detail': 'Callback sem code do Spotify.'}, status=400)

    credentials = f'{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}'
    basic = base64.b64encode(credentials.encode()).decode()
    token_response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={'Authorization': f'Basic {basic}'},
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        },
        timeout=10,
    )
    if token_response.status_code >= 400:
        return Response({'detail': 'Falha ao trocar code por token no Spotify.', 'spotify': token_response.text}, status=400)

    token_data = token_response.json()
    access_token = token_data['access_token']
    refresh_token = token_data.get('refresh_token', '')
    expires_at = timezone.now() + timedelta(seconds=token_data.get('expires_in', 3600))

    spotify_user_id = ''
    profile_response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    if profile_response.ok:
        spotify_user_id = profile_response.json().get('id', '')

    old_refresh = ''
    try:
        old_refresh = user.spotify_integration.refresh_token
    except SpotifyIntegration.DoesNotExist:
        pass

    SpotifyIntegration.objects.update_or_create(
        user=user,
        defaults={
            'spotify_user_id': spotify_user_id,
            'access_token': access_token,
            'refresh_token': refresh_token or old_refresh,
            'expires_at': expires_at,
            'is_active': True,
        },
    )
    pref = user.music_preference
    pref.enabled = True
    pref.save(update_fields=['enabled', 'updated_at'])
    return redirect(f'{settings.FRONTEND_URL}/?spotify=connected')



def _refresh_token(integration):
    credentials = f'{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}'
    basic = base64.b64encode(credentials.encode()).decode()
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={'Authorization': f'Basic {basic}'},
        data={'grant_type': 'refresh_token', 'refresh_token': integration.refresh_token},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    integration.access_token = data['access_token']
    integration.expires_at = timezone.now() + timedelta(seconds=data.get('expires_in', 3600))
    integration.save(update_fields=['access_token', 'expires_at', 'updated_at'])
    return integration


@api_view(['POST'])
def spotify_sync(request):
    try:
        integration = request.user.spotify_integration
    except SpotifyIntegration.DoesNotExist:
        return Response({'detail': 'Spotify não conectado.'}, status=400)

    if integration.expires_at <= timezone.now():
        try:
            integration = _refresh_token(integration)
        except requests.HTTPError:
            return Response({'detail': 'Não foi possível renovar o token do Spotify. Conecte novamente.'}, status=401)

    response = requests.get(
        'https://api.spotify.com/v1/me/player/currently-playing',
        headers={'Authorization': f'Bearer {integration.access_token}'},
        timeout=10,
    )

    # 204 = Spotify conectado, mas não há música ativa no momento.
    # Retornamos 200 com status limpo para o frontend remover a música antiga da tela.
    if response.status_code == 204:
        status_obj = clear_music_status(request.user)
        return Response(MusicStatusSerializer(status_obj).data)

    if response.status_code == 401:
        return Response({'detail': 'Token do Spotify expirado ou inválido. Conecte o Spotify novamente.'}, status=401)

    if response.status_code == 403:
        return Response({'detail': 'Spotify conectado sem permissão suficiente. Confira o scope user-read-currently-playing e conecte novamente.'}, status=403)

    if response.status_code == 429:
        return Response({'detail': 'Limite de requisições do Spotify atingido.'}, status=429)

    response.raise_for_status()
    data = response.json()
    item = data.get('item')

    if not item:
        status_obj = clear_music_status(request.user)
        return Response(MusicStatusSerializer(status_obj).data)

    artists = ', '.join([artist.get('name', '') for artist in item.get('artists', [])])
    album = item.get('album') or {}
    images = album.get('images') or []
    external_urls = item.get('external_urls') or {}

    status_obj, _ = UserMusicStatus.objects.get_or_create(user=request.user)
    previous_track_id = status_obj.spotify_track_id
    previous_is_playing = status_obj.is_playing
    previous_progress = status_obj.progress_ms

    status_obj.track_name = item.get('name', '')
    status_obj.artist_name = artists
    status_obj.album_name = album.get('name', '')
    status_obj.album_cover_url = images[0]['url'] if images else ''
    status_obj.spotify_url = external_urls.get('spotify', '')
    status_obj.spotify_track_id = item.get('id', '')
    status_obj.is_playing = data.get('is_playing', False)
    status_obj.progress_ms = data.get('progress_ms') or 0
    status_obj.duration_ms = item.get('duration_ms') or 0
    status_obj.last_played_at = timezone.now()
    status_obj.save()

    # Notifica em tempo real quando trocar faixa, pausar/tocar ou quando o progresso variar bastante.
    changed = (
        previous_track_id != status_obj.spotify_track_id
        or previous_is_playing != status_obj.is_playing
        or abs((previous_progress or 0) - (status_obj.progress_ms or 0)) > 15000
    )
    if changed:
        broadcast_music_status(request.user, status_obj)

    return Response(MusicStatusSerializer(status_obj).data)
