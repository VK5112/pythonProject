from django.contrib import admin
from .models import UserProfile, OrderModel, Comment

admin.site.register(UserProfile)
admin.site.register(OrderModel)
admin.site.register(Comment)
