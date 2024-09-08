from django.contrib.auth.models import User

from .models import UserProfile
from .serializers import UserSerializer



def create_user_service(data):
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save(is_active=False)

    profile_data = data.get('profile')

    if profile_data:
        user.userprofile.first_name = profile_data.get('first_name', user.first_name)
        user.userprofile.last_name = profile_data.get('last_name', user.last_name)
        user.userprofile.save()

    else:
        UserProfile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            role='manager'
        )

    return user

def get_users_service():
    return User.objects.all()
