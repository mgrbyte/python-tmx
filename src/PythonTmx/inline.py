from __future__ import annotations

from typing import Literal, MutableSequence, overload

from lxml.etree import Element, _Element
from typing_extensions import deprecated

_EmptyElem_ = Element("empty")


def _parse_inline(
    elem: _Element | None,
) -> MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] | str:
    """
    _summary_

    :param elem: _description_
    :type elem: _Element | None
    :return: _description_
    :rtype: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] | str
    """
    result: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] = []
    if elem is None:
        return result
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


class Bpt:
    content: MutableSequence[str | Sub]
    i: int
    x: int | None
    type: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        i: int,
        x: int | None = None,
        type: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param i: _description_
        :type i: int
        :param x: _description_, defaults to None
        :type x: int | None, optional
        :param type: _description_, defaults to None
        :type type: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.i = kwargs.get("i", elem.get("i"))
        self.x = kwargs.get("x", elem.get("x"))
        self.type = kwargs.get("type", elem.get("type"))
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


class Ept:
    content: str
    i: int | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        i: int | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param i: _description_, defaults to None
        :type i: int | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.i = kwargs.get("i", elem.get("i"))
        if isinstance(self.i, str):
            try:
                self.i = int(self.i)
            except (TypeError, ValueError):
                pass


class Hi:
    content: str
    x: int | None
    type: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        x: int | None = None,
        type: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param x: _description_, defaults to None
        :type x: int | None, optional
        :param type: _description_, defaults to None
        :type type: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.type = kwargs.get("type", elem.get("type"))
        self.x = kwargs.get("x", elem.get("x"))
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass


class It:
    content: str
    pos: Literal["begin", "end"]
    x: int | None
    type: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        pos: Literal["begin", "end"],
        x: int | None = None,
        type: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param pos: _description_
        :type pos: Literal[&quot;begin&quot;, &quot;end&quot;]
        :param x: _description_, defaults to None
        :type x: int | None, optional
        :param type: _description_, defaults to None
        :type type: str | None, optional
        """
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


class Ph:
    content: str
    x: int | None
    type: str | None
    assoc: Literal["p", "f", "b"] | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        content: str,
        x: int | None = None,
        type: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param x: _description_, defaults to None
        :type x: int | None, optional
        :param type: _description_, defaults to None
        :type type: str | None, optional
        :param assoc: _description_, defaults to None
        :type assoc: Literal[&quot;p&quot;, &quot;f&quot;, &quot;b&quot;] | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.x = kwargs.get("x", elem.get("x"))
        self.type = kwargs.get("type", elem.get("type"))
        self.pos = kwargs.get("pos", elem.get("pos"))
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass


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
        content: str,
        type: str | None = None,
        datatype: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param content: _description_
        :type content: str
        :param type: _description_, defaults to None
        :type type: str | None, optional
        :param datatype: _description_, defaults to None
        :type datatype: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.type = kwargs.get("type", elem.get("type"))
        self.datatype = kwargs.get("datatype", elem.get("datatype"))


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
        """
        _summary_

        :param content: _description_
        :type content: str
        :param x: _description_, defaults to None
        :type x: int | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.content = kwargs.get("content", _parse_inline(elem=elem))
        self.x = kwargs.get("x", elem.get("x"))
