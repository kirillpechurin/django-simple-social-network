from rest_framework import serializers

from users.models import User
from . import validators
from ...services.auth import AuthService


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, validators=[
        validators.PasswordValidator()
    ])
    password2 = serializers.CharField(required=True)

    email = serializers.EmailField(required=True)
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

    def validate_email(self, value):
        if User.objects.filter(email=User.objects.normalize_email(value)).exists():
            raise serializers.ValidationError("Email already exists.")
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
            last_name=validated_data["last_name"],
            email=validated_data["email"]
        )

        AuthService.request_confirm_email(user)
        return user


class ConfirmEmailSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)


class ResendConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        user = User.objects.filter(email=User.objects.normalize_email(attrs["email"])).first()
        if not user:
            raise serializers.ValidationError({
                "email": "User not found."
            })

        attrs["user"] = user
        return attrs
