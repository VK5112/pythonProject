from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name
