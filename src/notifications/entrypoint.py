from notifications.entrypoints import UserEntrypoint


class Handler:

    @classmethod
    def _get_entrypoint(cls, action: str):
        if action.startswith("USER_"):
            return UserEntrypoint()
        else:
            raise NotImplementedError

    @classmethod
    def accept(cls, action: str, **kwargs):
        entrypoint = cls._get_entrypoint(action)
        entrypoint.accept(action, **kwargs)
