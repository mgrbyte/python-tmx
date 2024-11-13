"""
This module contains all the inline elements of a tmx file.
They are the element that actually contain the text of the translation.
"""

# General Comment: We're intentionally letting users use the library without
# having to worry about type errors when creating a tmx object from scratch.
# Exorting to an Element though is much more strict and will raise an error if
# the user tries to do something that is not allowed.
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
    else:
        if not len(elem):
            return ""
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

    def __init__(self, **kwargs):
        if kwargs.get("elem") is not None:
            elem = kwargs.get("elem")
        else:
            elem = _Empty_Elem_
        if elem is not _Empty_Elem_:
            if elem.tag != self.__class__.__name__.lower():
                raise ValueError(
                    "provided element tag does not match the object you're "
                    "trying to create, expected "
                    f"<{self.__class__.__name__.lower()}> but got {elem.tag}"
                )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        for attr, value in locals()["kwargs"].items():
            if attr == "elem":
                continue
            if attr in self.__slots__:
                if attr in ("i", "x"):  # try to coerce int values
                    try:
                        setattr(self, attr, int(value))
                    except (ValueError, TypeError):
                        setattr(self, attr, value)
                elif attr == "content":  # parse content if needed using parse_inline
                    setattr(
                        self,
                        attr,
                        value if value is not None else _parse_inline(elem),
                    )
                else:
                    setattr(self, attr, value)
            else:  # We're permissive but only with value types, not attributes
                raise AttributeError(
                    f"Unexpected attribute '{attr}' for "
                    f"{self.__class__.__name__} Elements"
                )

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
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
        elif isinstance(self.i, int):
            elem.set("i", str(self.i))
        else:
            elem.set("i", self.i)

        # Optional Attributes
        if self.x is not None:
            if isinstance(self.x, int):
                elem.set("x", str(self.x))
            else:
                elem.set("x", self.x)
        if self.type is not None:
            elem.set("type", self.type)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, Sub):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Bpt Element"
                        )
        return elem


class Ept(Inline):
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
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
        elif isinstance(self.i, int):
            elem.set("i", str(self.i))
        else:
            elem.set("i", self.i)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, Sub):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Ept Element"
                        )
        return elem


class Hi(Inline):
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
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
                elem.set("x", str(self.x))
            else:
                elem.set("x", self.x)
        if self.type is not None:
            elem.set("type", self.type)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, (Bpt, Ept, It, Ph, Hi)):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Hi Element"
                        )
        return elem


class It(Inline):
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
        pos: Literal["begin", "end"] | None = None,
        x: int | None = None,
        type: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
        elif self.pos not in ("begin", "end"):
            raise ValueError(
                'Attribute "pos" must be one of "begin", "end"' f"but got {self.pos}"
            )
        elem.set("pos", self.pos)

        # Optional Attributes
        if self.x is not None:
            if isinstance(self.x, int):
                elem.set("x", str(self.x))
            else:
                elem.set("x", self.x)
        if self.type is not None:
            elem.set("type", self.type)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, Sub):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Ept Element"
                        )
        return elem


class Ph(Inline):
    """
    `Placeholder` - The `Ph` element is used to delimit a sequence of native
    standalone codes in the segment.
    """

    __slots__ = "content", "i", "x", "assoc"
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
        content: str | MutableSequence[str | Sub] | None = None,
        x: int | None = None,
        assoc: Literal["p", "f", "b"] | None = None,
    ) -> None:
        """
        Constructor method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
            if isinstance(self.x, int):
                elem.set("x", str(self.x))
            else:
                elem.set("x", self.x)
        if self.assoc is not None:
            if self.assoc not in ("p", "f", "b"):
                raise ValueError(
                    'Attribute "pos" must be one of "p", "f", "b"'
                    f"but got {self.assoc}"
                )
            elem.set("assoc", self.assoc)

        # Content
        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, Sub):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Ept Element"
                        )
        return elem


class Sub(Inline):
    """
    `Sub-flow` - The `Sub` element is used to delimit sub-flow text inside a
    sequence of native code, for example: the definition of a footnote or the
    text of title in a HTML anchor element.
    """

    __slots__ = "content", "type", "datatype"
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
        content: str | MutableSequence[str | Sub] | None = None,
        type: str | None = None,
        datatype: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, (Bpt, Ept, It, Hi, Ph)):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Ept Element"
                        )
        return elem


@deprecated(
    "The Ut element is deprecated, "
    "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
    "know with which element to replace it with."
)
class Ut(Inline):
    """
    `Unknown Tag` - The `ut` element is used to delimit a sequence of native
    unknown codes in the segment.

    This element has been DEPRECATED. Use the guidelines outlined in
    the Rules for Inline Elements section in the official TMX Spec to choose
    which inline element to used instead of `Ut`.
    https://www.gala-global.org/tmx-14b#ContentMarkup_Rules
    """

    __slots__ = "content", "x"
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
        content: str | MutableSequence[str | Sub] | None = None,
        x: int | None = None,
    ) -> None:
        """
        Constructor method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

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
            if isinstance(self.x, int):
                elem.set("x", str(self.x))
            else:
                elem.set("x", self.x)

        # Content
        if isinstance(self.content, str):
            elem.text = self.content
        else:
            for item in self.content:
                if isinstance(item, str):
                    # If elem has already has another inline, add or append
                    # the text as the tail of that element
                    if len(elem):
                        elem[-1].tail = (
                            elem[-1].tail + item if elem[-1].tail is not None else item
                        )
                    # If elem has no inline, add the text as the text of the element
                    else:
                        elem.text = elem.text + item if elem.text is not None else item
                else:
                    # else check if element is allowed and append it
                    if isinstance(item, Sub):
                        elem.append(item.to_element())
                    else:
                        raise ValueError(
                            f"'{type(item)}' Elements are not allowed inside a "
                            "Ept Element"
                        )
        return elem
