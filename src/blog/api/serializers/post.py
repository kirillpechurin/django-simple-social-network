from rest_framework import serializers

from blog.models import Post


class PostLikesSerializerMixin(metaclass=serializers.SerializerMetaclass):
    count_likes = serializers.SerializerMethodField(method_name="get_count_likes")

    def get_count_likes(self, post: Post) -> int:
        return post.likes.count()


class PostListSerializer(PostLikesSerializerMixin,
                         serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "content",
            "count_likes",
            "created_at",
            "updated_at"
        )


class PostSerializer(PostListSerializer):
    pass


class PostCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, max_length=500)

    def create(self, validated_data):
        post = Post.objects.create(
            user_id=self.context["request"].user.pk,
            content=validated_data["content"]
        )
        return post

    def to_representation(self, instance):
        return PostSerializer(instance).data


class PostUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, max_length=500)

    def update(self, post: Post, validated_data):
        post.content = validated_data.get("content", post.content)
        post.save()
        return post

    def to_representation(self, instance):
        return PostSerializer(instance).data
