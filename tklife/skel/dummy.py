

from typing import Mapping, Optional


class DummyAttr(object):
    def __init__(self, parent: Optional['DummyAttr'] = None, name: Optional[str] = None) -> None:
        self._descendants = {}
        self._parent = parent
        self._name = name

    def __getattr__(self, name: str):
        if name not in self._descendants:
            self._descendants[name] = self.__class__(parent=self, name=name)
        return self._descendants[name]

    def get_real(self, o: Mapping):
        attr_chain = []
        current_dummy = self
        while current_dummy._parent is not None:
            attr_chain.append(current_dummy._name)
            current_dummy = current_dummy._parent
        for attr in reversed(attr_chain):
            o = o[attr]
        return o

    def __repr__(self) -> str:
        """return self.attr_name"""
        return self._name


if __name__ == "__main__":
    o = {
        'hello': {
            'there': 'it works'
        }
    }
    d = DummyAttr()
    i = d.hi
    j = d.hello.there
    k = d.hello.world
    print(j.get_real(o))
