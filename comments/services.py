from rest_framework import serializers, status
from rest_framework.response import Response

from orders.models import STATUS_CHOICES, OrderModel
from .models import Comment


def create_comment_service(order, user, comment_data):
    comment_data.pop('order', None)
    comment_data.pop('user', None)

    if order.manager is not None and order.manager != user:
        raise serializers.ValidationError('You cannot comment on this order.')

    order.manager = user
    if order.status not in STATUS_CHOICES or order.status in [None, 'New']:
        order.status = 'In work'
    order.save()

    comment = Comment.objects.create(user=user, order=order, **comment_data)
    return comment


def get_comment_list_service(order_id):
    return Comment.objects.filter(order_id=order_id).order_by('-created_at')


def get_comment_list_with_order_info_service(order_id):
    comments = get_comment_list_service(order_id)
    order = OrderModel.objects.get(id=order_id)
    return {
        "comments": comments,
        "utm": order.utm,
        "msg": order.msg,
    }


def handle_create_comment(serializer, user):
    order = serializer.validated_data['order']
    comment = create_comment_service(order, user, serializer.validated_data)
    serializer.instance = comment
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def handle_list_comments(order_id, serializer_class):
    response_data = get_comment_list_with_order_info_service(order_id)
    serializer = serializer_class(response_data["comments"], many=True)
    response_data["comments"] = serializer.data
    return Response(response_data, status=status.HTTP_200_OK)
