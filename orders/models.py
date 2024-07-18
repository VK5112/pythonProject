from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


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

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        db_table = 'orders'
