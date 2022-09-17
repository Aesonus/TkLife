
from typing import ClassVar, Literal, TypedDict, Union


class TEntry(TypedDict, total=False):
    bordercolor: Union[str, tuple[Literal["disabled", "focus", "readonly"]]]
    darkcolor: str
    fieldbackground: str
    foreground: str
    insertcolor: str
    insertwidth: int
    lightcolor: str
    padding: int
    relief: str
    selectbackground: str
    selectborderwidth: int
    selectforeground: str

def test(ten: TEntry):
    pass

print(TEntry(bordercolor=('disabled',)))