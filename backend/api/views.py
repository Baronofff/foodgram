from djoser.views import UserViewSet as DjoserUserViewSet
from users.models import User
from api.serializers import UserSerializer


class UserViewSet(DjoserUserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )
