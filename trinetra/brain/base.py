class Brain:
    """A brain reads a disclosure entry and returns astra source code (str)."""
    name = "base"

    def draft_astra(self, entry) -> str:
        raise NotImplementedError
