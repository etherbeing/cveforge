class ForgeException(Exception):
    """Raise this exception to communicate withing the CLI, for example for an exit request or similar"""

    def __init__(self, *args: object, code: int = 0) -> None:
        super().__init__(*args)
        self.code = code

    code: int
