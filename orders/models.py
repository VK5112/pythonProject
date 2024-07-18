from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role='manager',
            username=instance.username,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )


@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    instance.userprofile.username = instance.username
    instance.userprofile.first_name = instance.first_name
    instance.userprofile.last_name = instance.last_name
    instance.userprofile.save()


class OrderModel(models.Model):
    name = models.CharField(max_length=120)
    surname = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=120)
    age = models.IntegerField()
    course = models.CharField(max_length=120)
    course_format = models.CharField(max_length=120)
    course_type = models.CharField(max_length=120)
    sum = models.IntegerField()
    alreadyPaid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    utm = models.CharField(max_length=120)
    msg = models.CharField(max_length=120)
    manager_username = models.CharField(max_length=150, blank=True, null=True)
    group = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        db_table = 'orders'
