from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={
            'role': 'manager',
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        })
    else:
        user_profile, created = UserProfile.objects.get_or_create(user=instance)
        user_profile.username = instance.username
        user_profile.first_name = instance.first_name
        user_profile.last_name = instance.last_name
        user_profile.save()
