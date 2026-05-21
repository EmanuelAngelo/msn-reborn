from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, UserMusicPreference, UserMusicStatus


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_defaults(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'display_name': instance.first_name or instance.username or instance.email.split('@')[0]},
        )
        UserMusicPreference.objects.get_or_create(user=instance)
        UserMusicStatus.objects.get_or_create(user=instance)
