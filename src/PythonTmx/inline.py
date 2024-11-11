from __future__ import annotations

from typing import Literal, MutableSequence, overload

from lxml.etree import Element, _Element
from typing_extensions import deprecated

from PythonTmx.utils import XmlElementLike

_EmptyElem_ = Element("empty")


def _add_attrs(): ...


def _parse_inline(
    elem: XmlElementLike,
) -> MutableSequence[str | Inline] | str:
    """
    Internal function that parses a inline element and outputs a list of strings and Inline Elements in document order.

    Parameters
    ----------
    elem : _Element
        The Element to parse.

    Returns
    -------
    MutableSequence[str | Inline] | str
         list of str and Inline Elements
    """
    result: MutableSequence[str | Inline] = []
    if elem.text:
        if not len(elem):
            return elem.text
        result.append(elem.text)
    for child in elem:
        match child.tag:
            case "bpt":
                result.append(Bpt(elem=child))
            case "ept":
                result.append(Ept(elem=child))
            case "it":
                result.append(It(elem=child))
            case "hi":
                result.append(Hi(elem=child))
            case "ph":
                result.append(Ph(elem=child))
            case "sub":
                result.append(Sub(elem=child))
            case "ut":
                result.append(Ut(elem=child))
            case _:
                pass
        if child.tail:
            result.append(child.tail)
    return result


class Inline:
    """
    Base class for Inline elements. Not meant to be instantiated and purely here
    for inheritance.
    """

    __slots__ = ("_source_elem",)

    _source_elem: XmlElementLike | None

    def __init__(self):
        raise NotImplementedError

    def to_element(self) -> _Element:
        raise NotImplementedError


class Bpt(Inline):
    """
    `Begin paired tag` - The `Bpt` element is used to delimit the beginning of
    a paired sequence of native codes. Each `Bpt` has a corresponding `Ept`
    element within the segment.
    """

    __slots__ = "content", "i", "x", "type"
    content: str | MutableSequence[str | Sub]
    """
    The actual content of the element.
    """
    i: int
    """
    Used to pair the `Bpt` elements with :class:`Ept` elements. This mechanism
    provides TMX with support to markup a possibly overlapping range of codes.
    Must be unique for each `Bpt` within a given
    `Tuv <PythonTmx.structural.html#structural.Tuv>`_ element.
    """
    x: int | None
    """
    Used to match inline elements between each
    `Tuv <PythonTmx.structural.html#structural.Tuv>`_ elements of a given
    `Tu <PythonTmx.structural.html#structural.Tu>`_ element.
    Note that an `Ept` element is matched based on the `x` attribute of its
    corresponding <bpt> element.
    """
    type: str | None
    """
    The kind of data the element represents.
    """

    def __init__(
        self,
        *,
        elem: _Element | None = None,
        content: str | MutableSequence[str | Sub] | None = None,
        i: int | None = None,
        x: int | None = None,
        type: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        elem = elem if elem is not None else _EmptyElem_
        self.content = content if content is not None else _parse_inline(elem)
        self.i = i if i is not None else elem.get("i", None)
        self.x = x if x is not None else elem.get("x", None)
        self.type = type if type is not None else elem.get("type", None)
        if isinstance(self.i, str):
            try:
                self.i = int(self.i)
            except (TypeError, ValueError):
                pass
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        elem = Element("bpt")
        elem.text, elem.tail = "", ""
        # Required Attributes
        if self.i is None:
            raise AttributeError("Attribute 'i' is required for Bpt Elements")
        elif isinstance(self.i, (int, str)):
            elem.set("i", str(self.i))

        # Optional Attributes
        if self.x is not None:
            elem.set("x", self.x)
        if self.type is not None:
            elem.set("type", self.type)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item
                    else:
                        elem.tail += item
                elif isinstance(item, Sub):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Bpt Element"
                    )
        return elem


class Ept:
    content: MutableSequence[str | Sub]
    i: int | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: MutableSequence[str | Sub],
        i: int | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.i = kwargs.get("i", elem.get("i"))
        if isinstance(self.i, str):
            try:
                self.i = int(self.i)
            except (TypeError, ValueError):
                pass

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("ept")
        _add_attrs(
            elem,
            {"i": self.i},
            tuple(),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, Sub):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Ept Element"
                    )
        return elem


class Hi:
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    x: int | None
    type: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: MutableSequence[str | Bpt | Ept | It | Ph | Hi],
        x: int | None = None,
        type: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.type = kwargs.get("type", elem.get("type"))
        self.x = kwargs.get("x", elem.get("x"))
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("hi")
        _add_attrs(
            elem,
            {"x": self.x, "type": self.type},
            tuple(),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, (Bpt, Ept, Hi, It, Ph)):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Hi Element"
                    )
        return elem


class It:
    content: MutableSequence[str | Sub]
    pos: Literal["begin", "end"]
    x: int | None
    type: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: MutableSequence[str | Sub],
        pos: Literal["begin", "end"],
        x: int | None = None,
        type: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.pos = kwargs.get("pos", elem.get("pos"))
        self.type = kwargs.get("type", elem.get("type"))
        self.x = kwargs.get("x", elem.get("x"))
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("it")
        _add_attrs(
            elem,
            {"pos": self.pos, "x": self.x, "type": self.type},
            ("pos",),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, Sub):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a It Element"
                    )
        return elem


class Ph:
    content: MutableSequence[str | Sub]
    x: int | None
    type: str | None
    assoc: Literal["p", "f", "b"] | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: MutableSequence[str | Sub],
        x: int | None = None,
        type: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.x = kwargs.get("x", elem.get("x"))
        self.type = kwargs.get("type", elem.get("type"))
        self.assoc = kwargs.get("assoc", elem.get("assoc"))
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("ph")
        _add_attrs(
            elem,
            {"x": self.x, "type": self.type, "assoc": self.assoc},
            tuple(),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, Sub):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Ph Element"
                    )
        return elem


class Sub:
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi] | str
    type: str | None
    datatype: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: MutableSequence[str | Sub],
        type: str | None = None,
        datatype: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.type = kwargs.get("type", elem.get("type"))
        self.datatype = kwargs.get("datatype", elem.get("datatype"))

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("sub")
        _add_attrs(
            elem,
            {"datatype": self.datatype, "type": self.type},
            tuple(),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, (Bpt, Ept, Hi, It, Ph)):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Sub Element"
                    )
        return elem


@deprecated(
    "The Ut element is deprecated, "
    "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
    "know with which element to replace it with."
)
class Ut:
    content: MutableSequence[str | Sub] | str
    x: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        x: int | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.x = kwargs.get("x", elem.get("x"))

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("ph")
        _add_attrs(
            elem,
            {"x": self.x},
            tuple(),
            force_str,
        )
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    if len(elem):
                        elem[-1].tail += item  # type:ignore
                    else:
                        elem.tail += item  # type:ignore
                elif isinstance(item, Sub):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise TypeError(
                        f"'{type(item)}' Elements are not allowed inside a Ut Element"
                    )
        return elem
