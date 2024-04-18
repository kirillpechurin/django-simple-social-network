from blog.models import PostComment, Post
from notifications import Handler as NotificationsHandler
from users.models import User


class PostCommentService:

    @staticmethod
    def create(post: Post,
               user: User,
               data: dict) -> PostComment:
        post_comment = PostComment.objects.create(
            post_id=post.pk,
            user_id=user.pk,
            comment=data["comment"]
        )

        NotificationsHandler.accept(
            action="BLOG_POSTS_NEW_COMMENT",
            data={
                "post": {
                    "id": post.pk,
                    "user_id": post.user_id
                },
                "from_user": {
                    "id": user.pk
                }
            }
        )
        return post_comment

    @staticmethod
    def update(post_comment: PostComment,
               data: dict) -> PostComment:
        post_comment.comment = data.get("comment", post_comment.comment)
        post_comment.save(update_fields=["comment"])
        return post_comment
