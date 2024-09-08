from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='manager')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        unique_together = ['user']

    def save(self, *args, **kwargs):
        if self.user.first_name != self.first_name or self.user.last_name != self.last_name:
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save()
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role='manager',
            first_name=instance.first_name,
            last_name=instance.last_name,
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.first_name = instance.first_name
        instance.userprofile.last_name = instance.last_name
        instance.userprofile.save()
