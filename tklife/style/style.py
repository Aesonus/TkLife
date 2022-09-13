

class _StyleMeta(type):

    def __new__(cls, name, bases, namespace):
        return super().__new__(cls, name, bases, namespace)

    @property
    def ttk_style(cls):
        return ".".join((cls.__name__, *(b.__name__ for b in cls.__bases__)))

class BaseStyle(metaclass=_StyleMeta):
    """All the base styles inherit from this class"""

class TEntry(BaseStyle):
    """This would be the base style. Extending this would add a new style type"""
