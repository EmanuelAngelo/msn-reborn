from .models import UserMusicPreference, UserProfile
from .serializers import MusicStatusSerializer, UserProfileSerializer


def get_public_status(profile):
    if profile.status == UserProfile.Status.INVISIBLE:
        return UserProfile.Status.OFFLINE
    return profile.status


def public_profile_payload(user, request=None):
    data = UserProfileSerializer(user.profile, context={'request': request}).data
    data['status'] = get_public_status(user.profile)
    return data


def public_music_payload(user):
    pref = user.music_preference
    status = user.music_status

    if not pref.enabled:
        return None

    if pref.visibility == UserMusicPreference.Visibility.PRIVATE:
        return None

    if not pref.show_when_paused and not status.is_playing:
        return None

    data = MusicStatusSerializer(status).data

    if not pref.show_album_cover:
        data['album_cover_url'] = ''

    if not pref.show_spotify_link:
        data['spotify_url'] = ''

    return data
