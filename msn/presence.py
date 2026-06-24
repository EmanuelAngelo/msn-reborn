from .models import UserProfile


def get_public_status(profile):
    if profile.status == UserProfile.Status.INVISIBLE:
        return UserProfile.Status.OFFLINE
    return profile.status
