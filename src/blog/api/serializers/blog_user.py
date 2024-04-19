from rest_framework import serializers

from users.models import User


class BlogUserSerializer(serializers.ModelSerializer):
    count_posts = serializers.SerializerMethodField(method_name="get_count_posts")
    count_subscribers = serializers.SerializerMethodField(method_name="get_count_subscribers")
    count_subscriptions = serializers.SerializerMethodField(method_name="get_count_subscriptions")

    def get_count_posts(self, user: User) -> int:
        return user.posts.count()

    def get_count_subscribers(self, user: User) -> int:
        return user.subscribers.count()

    def get_count_subscriptions(self, user: User) -> int:
        return user.subscriptions.count()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "personal_website_url",
            "count_posts",
            "count_subscribers",
            "count_subscriptions"
        )
