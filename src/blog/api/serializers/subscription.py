from rest_framework import serializers

from blog.models import Subscription
from users.models import User


class SubscriptionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username"
        )


class SubscriptionListSerializer(serializers.ModelSerializer):
    to_user = SubscriptionUserSerializer()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "to_user"
        )


class SubscriptionCreateSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField(required=True)


class SubscriberListSerializer(serializers.ModelSerializer):
    from_user = SubscriptionUserSerializer(source="user")

    class Meta:
        model = Subscription
        fields = (
            "id",
            "from_user"
        )
