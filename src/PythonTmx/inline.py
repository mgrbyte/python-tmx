from __future__ import annotations

from typing import Literal, MutableSequence

from lxml.etree import Element, _Element
from typing_extensions import deprecated

from PythonTmx import XmlElementLike

_Empty_Elem_ = Element("empty")


def _parse_inline(
    elem: XmlElementLike,
) -> MutableSequence[str | Inline] | str:
    """
    Internal function that parses a inline element and outputs a list of
    strings and Inline Elements in document order.

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
    if elem.text is not None:
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
    Base class for Inline elements. Doesn't contain any logic and is only
    here for inheritance.
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
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] | None = None,
        i: int | None = None,
        x: int | None = None,
        type: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "bpt":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'bpt' but got {elem.tag}"
            )
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
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
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
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a Bpt Element"
                    )
        return elem


class Ept:
    """
    `End paired tag` - The `Ept` element is used to delimit the end of a paired
    sequence of native codes. Each `Ept` has a corresponding `Bpt` element
    within the segment.
    """

    __slots__ = "content", "i"
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

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] | None = None,
        i: int | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "ept":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'ept' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.i = i if i is not None else elem.get("i", None)
        if isinstance(self.i, str):
            try:
                self.i = int(self.i)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("ept")
        elem.text, elem.tail = "", ""

        # Required Attributes
        if self.i is None:
            raise AttributeError("Attribute 'i' is required for Ept Elements")
        if isinstance(self.i, int):
            self.i = str(self.i)
        elem.set("i", self.i)

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
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a Ept Element"
                    )
        return elem


class Hi:
    """
    `Highlight` - The `Hi` element delimits a section of text that has special
    meaning, such as a terminological unit, a proper name, an item that should
    not be modified, etc. It can be used for various processing tasks. For
    example, to indicate to a Machine Translation tool proper names that should
    not be translated; for terminology verification, to mark suspect expressions
    after a grammar checking.
    """

    __slots__ = "content", "x", "type"

    content: str | MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    """
    The actual content of the element.
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
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Bpt | Ept | It | Ph | Hi] | None = None,
        x: int | None = None,
        type: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "hi":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'hi' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.x = x if x is not None else elem.get("x")
        self.type = type if type is not None else elem.get("type")
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("hi")
        elem.text, elem.tail = "", ""

        # Optional Attributes
        if self.x is not None:
            if isinstance(self.x, int):
                self.x = str(self.x)
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
                elif isinstance(item, (Bpt, Ept, It, Ph, Hi)):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a Hi Element"
                    )
        return elem


class It:
    """
    `Isolated tag` - The `It` element is used to delimit a beginning/ending
    sequence of native codes that does not have its corresponding
    ending/beginning within the segment.
    """

    __slots__ = "content", "pos", "x", "type"

    content: str | MutableSequence[str | Sub]
    """
    The actual content of the element.
    """
    pos: Literal["begin", "end"]
    """
    Whether an `It` element is a beginning or and ending element.
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
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] | None = None,
        pos: Literal["begin", "end"],
        x: int | None = None,
        type: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "it":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'it' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.pos = pos if pos is not None else elem.get("pos", None)
        self.x = x if x is not None else elem.get("x", None)
        self.type = type if type is not None else elem.get("type", None)
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("it")
        elem.text, elem.tail = "", ""

        # Required Attributes
        if self.pos is None:
            raise AttributeError("Attribute 'pos' is required for It Elements")
        if self.pos is None:
            raise AttributeError("Attribute 'pos' is required for Header Elements")
        elif self.pos.lower() not in ("begin", "end"):
            raise ValueError(
                'Attribute "pos" must be one of "begin", "end"'
                f"but got {self.pos.lower()}"
            )
        elem.set("pos", self.pos.lower())

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
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a It Element"
                    )
        return elem


class Ph:
    """
    `Placeholder` - The `Ph` element is used to delimit a sequence of native
    standalone codes in the segment.
    """

    content: str | MutableSequence[str | Sub]
    """
    The actual content of the element.
    """
    i: int | None
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
    assoc: Literal["p", "f", "b"] | None
    """
    The association of a `Ph` with the text prior or after.
    "p" (the element is associated with the text preceding the element),
    "f" (the element is associated with the text following the element), or
    "b" (the element is associated with the text on both sides).
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] = None,
        x: int | None = None,
        type: str | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "ph":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'ph' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.x = x if x is not None else elem.get("x", None)
        self.assoc = assoc if assoc is not None else elem.get("assoc", None)
        self.type = type if type is not None else elem.get("type", None)
        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("ph")
        elem.text, elem.tail = "", ""

        # Optional Attributes
        if self.x is not None:
            elem.set("x", self.x)
        if self.type is not None:
            elem.set("type", self.type)
        if self.assoc is not None:
            if self.assoc.lower() not in ("p", "f", "b"):
                raise ValueError(
                    'Attribute "pos" must be one of "p", "f", "b"'
                    f"but got {self.assoc.lower()}"
                )
            elem.set("assoc", self.assoc.lower())

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
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a It Element"
                    )
        return elem


class Sub:
    """
    `Sub-flow` - The `Sub` element is used to delimit sub-flow text inside a
    sequence of native code, for example: the definition of a footnote or the
    text of title in a HTML anchor element.
    """

    content: str | MutableSequence[str | Bpt | Ept | It | Ph | Hi]
    """
    The actual content of the element.
    """
    type: str | None
    """
    The kind of data the element represents.
    """
    datatype: str | None
    """
    The type of data contained in the element.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] = None,
        type: str | None = None,
        datatype: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "sub":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'sub' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.datatype = datatype if datatype is not None else elem.get("datatype", None)
        self.type = type if type is not None else elem.get("type", None)

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("sub")
        elem.text, elem.tail = "", ""

        # Optional Attributes
        if self.type is not None:
            elem.set("type", self.type)
        if self.datatype is not None:
            elem.set("datatype", self.datatype)

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
                elif isinstance(item, (Bpt, Ept, It, Ph, Hi)):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a Sub Element"
                    )
        return elem


@deprecated(
    "The Ut element is deprecated, "
    "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
    "know with which element to replace it with."
)
class Ut:
    """
    `Unknown Tag` - The `ut` element is used to delimit a sequence of native
    unknown codes in the segment.

    This element has been DEPRECATED. Use the guidelines outlined in
    the Rules for Inline Elements section in the official TMX Spec to choose
    which inline element to used instead of `Ut`.
    https://www.gala-global.org/tmx-14b#ContentMarkup_Rules
    """

    content: str | MutableSequence[str | Sub]
    """
    The actual content of the element.
    """
    x: int | None
    """
    Used to match inline elements between each
    `Tuv <PythonTmx.structural.html#structural.Tuv>`_ elements of a given
    `Tu <PythonTmx.structural.html#structural.Tu>`_ element.
    Note that an `Ept` element is matched based on the `x` attribute of its
    corresponding <bpt> element.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        *,
        content: str | MutableSequence[str | Sub] = None,
        x: int | None = None,
    ) -> None:
        """
        Constructor method
        """
        if elem is not _Empty_Elem_ and elem.tag != "ut":
            raise ValueError(
                "provided element tag does not match the object you're trying to create."
                f"expected 'ut' but got {elem.tag}"
            )
        self.content = content if content is not None else _parse_inline(elem)
        self.x = x if x is not None else elem.get("x", None)

        if isinstance(self.x, str):
            try:
                self.x = int(self.x)
            except (TypeError, ValueError):
                pass

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file
            or manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        ValueError
            Raised if :attr:`content` contains a disallowed element
        """
        elem = Element("sub")
        elem.text, elem.tail = "", ""

        # Optional Attributes
        if self.x is not None:
            elem.set("x", self.x)

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
                elif isinstance(item, (Bpt, Ept, It, Ph, Hi)):
                    elem.append(item.to_element())
                    elem[-1].tail = ""
                else:
                    raise ValueError(
                        f"'{type(item)}' Elements are not allowed inside a Sub Element"
                    )
        return elem
