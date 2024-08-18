from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(pre_save, sender=User)
def sync_user_first_last_name(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.first_name != instance.first_name or old_user.last_name != instance.last_name:
                UserProfile.objects.filter(user=instance).update(
                    first_name=instance.first_name,
                    last_name=instance.last_name
                )
        except User.DoesNotExist:
            pass


@receiver(pre_save, sender=UserProfile)
def sync_profile_first_last_name(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_profile = UserProfile.objects.get(pk=instance.pk)
            if old_profile.first_name != instance.first_name or old_profile.last_name != instance.last_name:
                User.objects.filter(pk=instance.user.pk).update(
                    first_name=instance.first_name,
                    last_name=instance.last_name
                )
        except UserProfile.DoesNotExist:
            pass
