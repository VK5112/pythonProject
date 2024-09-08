from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def sync_user_first_last_name(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.first_name = instance.first_name
        instance.userprofile.last_name = instance.last_name
        instance.userprofile.save()


@receiver(post_save, sender=UserProfile)
def sync_profile_first_last_name(sender, instance, **kwargs):
    user = instance.user
    user.first_name = instance.first_name
    user.last_name = instance.last_name
    user.save()