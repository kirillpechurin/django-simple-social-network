class Handler:

    @classmethod
    def accept(cls, action: str, **kwargs):
        raise NotImplementedError
