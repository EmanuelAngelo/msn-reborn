from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ContactRequestViewSet, ContactViewSet, ConversationViewSet,
    csrf, login_view, logout_view, me, music_preferences, music_status,
    register, search_users, update_my_status, spotify_callback, spotify_connect, spotify_sync,
)

router = DefaultRouter()
router.register('contacts', ContactViewSet, basename='contacts')
router.register('contact-requests', ContactRequestViewSet, basename='contact-requests')
router.register('conversations', ConversationViewSet, basename='conversations')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', csrf),
    path('auth/register/', register),
    path('auth/login/', login_view),
    path('auth/logout/', logout_view),
    path('me/', me),
    path('me/status/', update_my_status),
    path('users/search/', search_users),
    path('music/preferences/', music_preferences),
    path('music/status/', music_status),
    path('spotify/connect/', spotify_connect),
    path('spotify/callback/', spotify_callback),
    path('spotify/sync/', spotify_sync),
]
