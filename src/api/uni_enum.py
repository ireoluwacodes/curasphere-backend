import enum
import random


class BaseEnum(
    str, enum.Enum
):  # Inherit from `str` to make it JSON serializable
    def __str__(self):
        return self.value  # Ensures JSON responses return string values

    @classmethod
    def random(cls):
        """Return a random enum value from the subclass."""
        return random.choice(list(cls))
