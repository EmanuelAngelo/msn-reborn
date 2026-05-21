from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, UserProfile, ContactRequest, Contact, Conversation,
    ConversationParticipant, Message, PresenceSession, SpotifyIntegration,
    UserMusicPreference, UserMusicStatus,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'is_staff', 'is_active')
    ordering = ('email',)


admin.site.register(UserProfile)
admin.site.register(ContactRequest)
admin.site.register(Contact)
admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(PresenceSession)
admin.site.register(SpotifyIntegration)
admin.site.register(UserMusicPreference)
admin.site.register(UserMusicStatus)
