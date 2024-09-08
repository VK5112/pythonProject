from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Comment(models.Model):
    order = models.ForeignKey('orders.OrderModel', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)