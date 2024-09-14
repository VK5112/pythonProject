from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from orders.models import OrderModel


def get_order_statistics_service():
    total_count = OrderModel.objects.count()
    statuses = OrderModel.objects.values('status').annotate(count=Count('status'))
    null_count = OrderModel.objects.filter(status__isnull=True).count()

    status_counts = {status['status']: status['count'] for status in statuses}
    status_counts[None] = null_count

    for status in ['In work', 'New', 'Agree', 'Disagree', 'Dubbing', None]:
        if status not in status_counts:
            status_counts[status] = 0

    sorted_statuses = sorted(status_counts.items(), key=lambda x: (x[0] is not None, str(x[0])))

    result = {
        'total_count': total_count,
        'statuses': [{'status': status if status is not None else 'null', 'count': count} for status, count in sorted_statuses]
    }

    return result


def get_user_order_statistics_service(user_id):
    user = User.objects.get(pk=user_id)
    orders = OrderModel.objects.filter(manager=user)
    statuses = orders.values('status').annotate(count=Count('status'))

    result = {
        'total_count': orders.count(),
        'statuses': [{'status': status['status'], 'count': status['count']} for status in statuses]
    }

    return result


def ban_user_service(user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        return Response({'detail': f'User {user.first_name} {user.last_name} has been banned'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


def unban_user_service(user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        return Response({'detail': f'User {user.first_name} {user.last_name} has been unbanned'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


def generate_activation_token_service(user_id):
    user = User.objects.get(pk=user_id)
    if not user.is_active:
        refresh_token = RefreshToken.for_user(user)
        return str(refresh_token)
    else:
        raise serializers.ValidationError("User is already active")


def handle_generate_token_or_error(user_id):
    try:
        token = generate_activation_token_service(user_id)
        return Response({"token": token}, status=status.HTTP_200_OK)
    except serializers.ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)