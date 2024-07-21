import django_filters
from .models import OrderModel, COURSE_CHOICES, COURSE_FORMAT_CHOICES, COURSE_TYPE_CHOICES, STATUS_CHOICES


class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    surname = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    age = django_filters.NumberFilter()
    course = django_filters.ChoiceFilter(choices=[(choice, choice) for choice in COURSE_CHOICES])
    course_format = django_filters.ChoiceFilter(choices=[(choice, choice) for choice in COURSE_FORMAT_CHOICES])
    course_type = django_filters.ChoiceFilter(choices=[(choice, choice) for choice in COURSE_TYPE_CHOICES])
    status = django_filters.ChoiceFilter(choices=[(choice, choice) for choice in STATUS_CHOICES])
    group = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateTimeFilter()

    class Meta:
        model = OrderModel
        fields = ['name', 'surname', 'email', 'phone', 'age', 'course', 'course_format', 'course_type', 'status',
                  'group', 'created_at']
