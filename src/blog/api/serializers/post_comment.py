from rest_framework import serializers

from blog.models import PostComment
from users.models import User


class PostCommentFromUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username"
        )


class PostCommentListSerializer(serializers.ModelSerializer):
    from_user = PostCommentFromUserSerializer(source="user")

    class Meta:
        model = PostComment
        fields = (
            "id",
            "from_user",
            "comment"
        )


class PostCommentSerializer(serializers.ModelSerializer):
    from_user = PostCommentFromUserSerializer(source="user")

    class Meta:
        model = PostComment
        fields = (
            "id",
            "from_user",
            "comment"
        )


class PostCommentCreateSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True)

    def create(self, validated_data):
        return PostComment.objects.create(
            post_id=self.context["post_id"],
            user_id=self.context["request"].user.pk,
            comment=validated_data["comment"]
        )

    def to_representation(self, instance):
        return PostCommentSerializer(instance, context=self.context).data


class PostCommentUpdateSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get("comment", instance.comment)
        instance.save(update_fields=["comment"])
        return instance

    def to_representation(self, instance):
        return PostCommentSerializer(instance, context=self.context).data
