from rest_framework import serializers

from users.models import User
from . import validators


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[
        validators.PasswordValidator()
    ])
    password2 = serializers.CharField(required=True)

    class Meta:
        validators = [
            validators.PasswordEqualValidator()
        ]

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("Current password invalid.")
        return value

    def update(self, user: User, validated_data):
        user.set_password(validated_data["password"])
        user.save(update_fields=["password"])
        return user


class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[
        validators.PasswordValidator()
    ])
    password2 = serializers.CharField(required=True)

    class Meta:
        validators = [
            validators.PasswordEqualValidator()
        ]
