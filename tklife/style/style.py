import enum

__all__ = [
    'StyleEnum'
]

class StyleEnum(enum.Enum):
    """Holds the definition of styles"""

    def __init__(self) -> None:
        pass

    @property
    def tkstyle_name(self):
        pass

    @property
    def normal_styles(self):
        pass

    @property
    def dynamic_styles(self):
        pass
