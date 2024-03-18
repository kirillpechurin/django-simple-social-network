from rest_framework import serializers

from users.models import User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "personal_website_url",
            "address"
        )


class AccountUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, allow_blank=True)
    personal_website_url = serializers.URLField(required=True, allow_null=True)
    address = serializers.CharField(required=True, max_length=255, allow_null=True)

    def update(self, user: User, validated_data):
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.email = validated_data["email"]
        user.personal_website_url = validated_data["personal_website_url"]
        user.address = validated_data["address"]
        user.save(update_fields=[
            "first_name",
            "last_name",
            "email",
            "personal_website_url",
            "address",
        ])
        return user

    def to_representation(self, instance):
        return AccountSerializer(instance).data
