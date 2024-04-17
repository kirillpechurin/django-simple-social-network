from rest_framework import serializers

from notifications.models import SystemNotification


class SystemNotificationSerializer(serializers.ModelSerializer):
    payload = serializers.SerializerMethodField(method_name="get_payload")

    def get_payload(self, notification: SystemNotification) -> dict:
        return notification.payload

    class Meta:
        model = SystemNotification
        fields = (
            "id",
            "type_id",
            "event_id",
            "message",
            "is_read",
            "payload",
            "created_at",
            "updated_at"
        )


class SystemNotificationReadSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(required=True),
        required=True,
        allow_empty=False
    )
