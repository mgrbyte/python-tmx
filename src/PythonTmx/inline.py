"""
This module contains all the inline elements of a tmx file.
They are the element that actually contain the text of the translation.
"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import Literal

from lxml.etree import Element, _Element
from typing_extensions import deprecated

from PythonTmx import XmlElementLike
from PythonTmx.utils import _export_int, _parse_int_attr

EmptyElement = Element("empty")


def _parse_inline(
  elem: XmlElementLike | None,
) -> MutableSequence[str | Inline] | str:
  result: MutableSequence[str | Inline] = []
  if elem is None:
    return result
  if elem.text is not None:
    if not len(elem):
      return elem.text
    result.append(elem.text)
  else:
    if not len(elem):
      return result
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


def _export_inline(
  elem: _Element,
  content: MutableSequence[str | Inline] | str,
  force_str: bool,
) -> None:
  if elem.tag in ("bpt", "ept", "it", "ph", "ut"):
    allowed_tags = {"sub"}
  else:
    allowed_tags = {"bpt", "ept", "it", "ph", "hi", "ut"}
  for item in content:
    if isinstance(item, Inline):
      if item.__class__.__name__.lower() not in allowed_tags:
        raise ValueError(
          f"Invalid inline element {item.__class__.__name__}"
          " not allowed in this context"
        )
      elem.append(item.to_element(force_str))
    elif isinstance(item, str):
      if not len(elem):
        if not elem.text:
          elem.text = item
        else:
          elem.text += item
      else:
        if not elem[-1].tail:
          elem[-1].tail = item
        else:
          elem[-1].tail += item
    else:
      raise TypeError(f"Invalid SubElement, expected str or Inline, got {type(item)}")


class Inline:
  """
  Base class for Inline elements. Doesn't contain any logic and is only
  here for inheritance.
  """

  __slots__ = ("_source_elem",)

  _source_elem: XmlElementLike | None

  def __init__(self, elem: XmlElementLike | None = None, strict: bool = True, **kwargs):
    # Check element's tag, Error if it doesn't match the object's tag and
    # strict mode is enabled else try to create the object still
    if elem is not None:
      if str(elem.tag) != self.__class__.__name__.lower() and strict:
        raise ValueError(
          "provided element tag does not match the object you're "
          "trying to create, expected "
          f"<{self.__class__.__name__.lower()}> but got {str(elem.tag)}"
        )
      self._source_elem = elem
    else:
      self._source_elem = None
      elem = EmptyElement

    # Set attributes from kwargs or from the element's attributes if not
    # present in kwargs
    for attr, value in kwargs.items():
      match attr:
        case x if x not in self.__slots__:
          raise AttributeError(
            f"Attribute {attr} not allowed on " f"{self.__class__.__name__} objects"
          )
        case "i" | "x":  # handle int separately
          setattr(self, attr, _parse_int_attr(elem, attr, value))
        case "content":  # parse content using parse_inline
          (
            setattr(
              self,
              attr,
              value if value is not None else _parse_inline(elem),
            )
          )
        case _:
          setattr(self, attr, value if value is not None else elem.get(attr))

  def to_element(self, force_str: bool = False) -> _Element:
    elem = Element(self.__class__.__name__.lower())
    for attr in self.__slots__:
      val = getattr(self, attr)
      if val is None:
        continue
      match attr:
        case "x" | "i":  # handle int separately
          try:
            val = _export_int(attr, val)
          except ValueError as e:
            if not force_str:
              raise e
          elem.set(attr, val)
        case "content":
          if isinstance(val, str):
            elem.text = val
          else:
            _export_inline(elem, val, force_str)
        case _:
          if not isinstance(val, str):
            if not force_str:
              raise TypeError(f"Invalid value for '{attr}'. {val} is not a string")
            val = str(val)
          elem.set(attr, val)
    return elem


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

  def to_element(self, force_str: bool = False) -> _Element:
    # Required Attributes
    if self.i is None:
      raise AttributeError("Attribute 'i' is required for Bpt Elements")
    return super().to_element(force_str)


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

  def to_element(self, force_str: bool = False) -> _Element:
    # Required Attributes
    if self.i is None:
      raise AttributeError("Attribute 'i' is required for Ept Elements")
    return super().to_element(force_str)


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

  def to_element(self, force_str: bool = False) -> _Element:
    # Required Attributes
    if self.pos is None:
      raise AttributeError("Attribute 'pos' is required for It Elements")
    return super().to_element(force_str)


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
    i: int | None = None,
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
