from rest_framework import serializers

from users.models import User
from . import validators


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, validators=[
        validators.PasswordValidator()
    ])
    password2 = serializers.CharField(required=True)

    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        validators = [
            validators.PasswordEqualValidator()
        ]

    def validate_username(self, value):
        if User.objects.filter(username=User.normalize_username(value)).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Password invalid."
            })
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        return user
