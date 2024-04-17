class Handler:

    @classmethod
    def _get_entrypoint(cls, action: str):
        from notifications.entrypoints import (
            UserEntrypoint,
            BlogPostsEntrypoint
        )

        if action.startswith("USER_"):
            return UserEntrypoint()
        elif action.startswith("BLOG_POSTS"):
            return BlogPostsEntrypoint()
        else:
            raise NotImplementedError

    @classmethod
    def accept(cls, action: str, **kwargs):
        entrypoint = cls._get_entrypoint(action)
        entrypoint.accept(action, **kwargs)
