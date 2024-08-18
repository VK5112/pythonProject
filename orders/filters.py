import django_filters
from .models import OrderModel


class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    surname = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    age = django_filters.NumberFilter()
    course = django_filters.CharFilter(lookup_expr='icontains')
    course_format = django_filters.CharFilter(lookup_expr='icontains')
    course_type = django_filters.CharFilter(lookup_expr='icontains')
    sum = django_filters.NumberFilter()
    alreadyPaid = django_filters.NumberFilter()
    created_at = django_filters.DateFilter()
    status = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.CharFilter(lookup_expr='icontains')
    manager = django_filters.CharFilter(field_name='manager__first_name', lookup_expr='icontains')

    class Meta:
        model = OrderModel
        fields = ['name', 'surname', 'email', 'phone', 'age', 'course', 'course_format', 'course_type',
                  'sum', 'alreadyPaid', 'created_at', 'status', 'group', 'manager']
