from unittest.mock import patch

from django.test import TestCase

from notifications import Handler


class NotificationsEntrypointIntegrationTestCase(TestCase):

    def _call(self,
              action: str,
              **kwargs):
        Handler.accept(action, **kwargs)

    def test_user_confirm_email(self):
        with patch("notifications.entrypoints.user.UserEntrypoint.accept") as mock:
            self._call(
                action="USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )
            mock.assert_called_once_with(
                "USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )

    def test_user_forgot_password(self):
        with patch("notifications.entrypoints.user.UserEntrypoint.accept") as mock:
            self._call(
                action="USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )
            mock.assert_called_once_with(
                "USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )

    def test_blog_posts_like(self):
        with patch("notifications.entrypoints.blog_posts.BlogPostsEntrypoint.accept") as mock:
            self._call(
                action="BLOG_POSTS_LIKE",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )
            mock.assert_called_once_with(
                "BLOG_POSTS_LIKE",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )

    def test_blog_posts_like_remove(self):
        with patch("notifications.entrypoints.blog_posts.BlogPostsEntrypoint.accept") as mock:
            self._call(
                action="BLOG_POSTS_LIKE_REMOVE",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )
            mock.assert_called_once_with(
                "BLOG_POSTS_LIKE_REMOVE",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )

    def test_blog_posts_new_comment(self):
        with patch("notifications.entrypoints.blog_posts.BlogPostsEntrypoint.accept") as mock:
            self._call(
                action="BLOG_POSTS_NEW_COMMENT",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )
            mock.assert_called_once_with(
                "BLOG_POSTS_NEW_COMMENT",
                data={
                    "post": {
                        "id": 1,
                        "user_id": 1,
                    },
                    "from_user": {
                        "id": 2
                    }
                }
            )

    def test_blog_subscriptions_new(self):
        with patch("notifications.entrypoints.blog_subscriptions.BlogSubscriptionsEntrypoint.accept") as mock:
            self._call(
                action="BLOG_SUBSCRIPTIONS_NEW",
                data={
                    "to_user": {
                        "id": 1,
                    },
                    "from_user": {
                        "id": 2,
                        "username": "sample"
                    }
                }
            )
            mock.assert_called_once_with(
                "BLOG_SUBSCRIPTIONS_NEW",
                data={
                    "to_user": {
                        "id": 1,
                    },
                    "from_user": {
                        "id": 2,
                        "username": "sample"
                    }
                }
            )

    def test_blog_posts_new(self):
        with patch("notifications.entrypoints.blog_posts.BlogPostsEntrypoint.accept") as mock:
            self._call(
                action="BLOG_POSTS_NEW",
                data={
                    "post": {
                        "id": 1,
                        "user": {
                            "id": 1,
                            "username": "sample"
                        },
                    },
                    "to_user_ids": [1,2,3]
                }
            )
            mock.assert_called_once_with(
                "BLOG_POSTS_NEW",
                data={
                    "post": {
                        "id": 1,
                        "user": {
                            "id": 1,
                            "username": "sample"
                        },
                    },
                    "to_user_ids": [1,2,3]
                }
            )

    def test_unknown_action(self):
        self.assertRaises(NotImplementedError, self._call, action="UNKNOWN_ACTION", data={})
