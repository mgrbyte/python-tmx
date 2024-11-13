from collections.abc import Generator
from typing import Protocol, Self, TypeVar

T = TypeVar("T")


class XmlElementLike(Protocol):
    """
    Protocol for all ``elem`` attributes used in PythonTmx. Any class that
    follows this protocol can be used as replacement for an lxml ``_Element``
    in the context of this library.
    """

    tag: str
    """
    The tag if the xml Element.
    """
    text: str | None
    """
    The text of the Element, if any.
    """
    tail: str | None
    """
    The tail (text `after` the closing tag) of the Element, if any.
    """

    def __init__(self):
        self.tag = "empty"
        self.text = ""
        self.tail = ""

    def get(self, key: str, default: T | None = None) -> str | T:
        """
        Should any of the element's attribute using a key, and providing a
        default if the key doesn't exists.
        """
        ...

    def find(self, tag: str) -> Self | None:
        """
        Should return the first child element with the given tag.
        """
        ...

    def __iter__(self) -> Generator[Self, None, None]:
        """
        Should yield all direct children and all children should be of the same
        type.
        """
        ...

    def __len__(self) -> int:
        """
        Should return the amount of sub elements when calling ``len(element)``
        """


_Empty_Elem_ = XmlElementLike()
