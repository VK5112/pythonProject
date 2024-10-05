from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

STATUS_CHOICES = ['In work', 'New', 'Agree', 'Disagree', 'Dubbing']
COURSE_CHOICES = ['FS', 'QACX', 'JCX', 'JSCX', 'FE', 'PCX']
COURSE_TYPE_CHOICES = ['pro', 'minimal', 'premium', 'incubator', 'vip']
COURSE_FORMAT_CHOICES = ['static', 'online']


class OrderModel(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    surname = models.CharField(max_length=120, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=120, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    course = models.CharField(max_length=120, blank=True, null=True)
    course_format = models.CharField(max_length=120, blank=True, null=True)
    course_type = models.CharField(max_length=120, blank=True, null=True)
    sum = models.IntegerField(blank=True, null=True)
    alreadyPaid = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    utm = models.CharField(max_length=120, blank=True, null=True)
    msg = models.CharField(max_length=120, blank=True, null=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    group = models.CharField(max_length=120, blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.status and self.status not in STATUS_CHOICES:
            raise ValidationError(f'Status must be one of {STATUS_CHOICES}')
        if self.course and self.course not in COURSE_CHOICES:
            raise ValidationError(f'Course must be one of {COURSE_CHOICES}')
        if self.course_format and self.course_format not in COURSE_FORMAT_CHOICES:
            raise ValidationError(f'Course format must be one of {COURSE_FORMAT_CHOICES}')
        if self.course_type and self.course_type not in COURSE_TYPE_CHOICES:
            raise ValidationError(f'Course type must be one of {COURSE_TYPE_CHOICES}')

    def save(self, *args, **kwargs):
        self.clean()
        super(OrderModel, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        db_table = 'orders'
