"""
This module contains all the structural elements of a tmx file.
They are the building blocks of a tmx file.
"""

from collections.abc import Generator, MutableSequence
from datetime import datetime
from typing import Literal, no_type_check

from lxml.etree import Element, SubElement, _Element

from PythonTmx import XmlElementLike
from PythonTmx.inline import Bpt, Ept, Inline, _parse_inline
from PythonTmx.utils import (
    _export_dt,
    _export_int,
    _parse_dt_attr,
    _parse_int_attr,
)

EmptyElement = Element("empty")


def _check_seg(seg: MutableSequence[str | Inline] | str) -> None:
    if isinstance(seg, str):
        return
    bpt_i_list: list[int] = []
    ept_i_list: list[int] = []
    for item in seg:
        if isinstance(item, Bpt):
            if item.i in bpt_i_list:
                raise ValueError(f"Duplicate Bpt with i={item.i}")
            bpt_i_list.append(item.i)
        elif isinstance(item, Ept):
            if item.i in ept_i_list:
                raise ValueError(f"Duplicate Ept with i={item.i}")
            ept_i_list.append(item.i)
        elif isinstance(item, str):
            pass
        else:
            raise ValueError(f"Invalid item in segment: {item}")
    if len(bpt_i_list) > len(set(bpt_i_list)):
        raise ValueError("Too many Bpt")
    if len(ept_i_list) < len(set(ept_i_list)):
        raise ValueError("Too many Ept")
    for i in bpt_i_list:
        if i not in ept_i_list:
            raise ValueError(f"Bpt with i={i} is not followed by an Ept")


class Structural:
    """
    Base class for Structural elements. DO NOT USE THIS CLASS DIRECTLY.
    """

    __slots__ = ("_source_elem",)

    _source_elem: XmlElementLike | None

    def __init__(
        self, elem: XmlElementLike | None = None, strict: bool = True, **kwargs
    ):
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
                        f"Attribute {attr} not allowed on "
                        f"{self.__class__.__name__} objects"
                    )
                case "text":  # get text from element's text not through .get
                    setattr(self, attr, value if value is not None else elem.text)
                case "header":  # create an empty header if no value
                    if value is None:
                        if elem is not None:
                            setattr(self, attr, Header(elem=elem.find("header")))
                        else:
                            setattr(self, attr, Header())
                    else:
                        setattr(self, attr, value)
                case (
                    "creationdate"
                    | "changedate"
                    | "lastusagedate"
                ):  # Handle potential datetime separately
                    setattr(self, attr, _parse_dt_attr(elem, attr, value))
                case "lang":  # get lang from xml:lang attribute
                    setattr(
                        self,
                        attr,
                        value
                        if value is not None
                        else elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
                    )
                case "encoding" | "tmf":  # handle o- style attributes separately
                    setattr(
                        self,
                        attr,
                        value if value is not None else elem.get(f"o-{attr}"),
                    )
                case "usagecount":  # handle int separately
                    setattr(self, attr, _parse_int_attr(elem, attr, value))
                case "segment":  # parse segment using parse_inline
                    setattr(
                        self,
                        attr,
                        value if value is not None else _parse_inline(elem.find("seg")),
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
                case "creationdate" | "changedate" | "lastusagedate":
                    try:
                        val = _export_dt(attr, val)
                    except ValueError as e:
                        if not force_str:
                            raise e
                    elem.set(attr, val)
                case "usagecount":
                    try:
                        val = _export_int(attr, val)
                    except ValueError as e:
                        if not force_str:
                            raise e
                    elem.set(attr, val)
                case "lang":
                    if not isinstance(val, str):
                        if not force_str:
                            raise TypeError(
                                f"Invalid value for '{attr}'. {val} is not a string"
                            )
                        val = str(val)
                    elem.set("{http://www.w3.org/XML/1998/namespace}lang", val)
                case "tmf" | "encoding":
                    if not isinstance(val, str):
                        if not force_str:
                            raise TypeError(
                                f"Invalid value for '{attr}'. {val} is not a string"
                            )
                        val = str(val)
                    elem.set(f"o-{attr}", val)
                case "notes" | "props" | "tuvs" | "tus" | "udes" | "maps" | "header":
                    continue
                case "text":
                    elem.text = val
                case "segment":
                    if isinstance(val, str):
                        SubElement(elem, "seg").text = val
                case _:
                    if not isinstance(val, str):
                        if not force_str:
                            raise TypeError(
                                f"Invalid value for '{attr}'. {val} is not a string"
                            )
                        val = str(val)
                    elem.set(attr, val)
        return elem

    def __getitem__(self, key: str) -> str | None:
        if key in self.__slots__:
            return getattr(self, key)
        else:
            raise KeyError(f"'{key}' is not an attribute of {self.__class__.__name__}")

    def __setitem__(self, key: str, value: str | None) -> None:
        if key in self.__slots__:
            setattr(self, key, value)
        else:
            raise KeyError(f"'{key}' is not an attribute of {self.__class__.__name__}")

    def __delitem__(self, key: str) -> None:
        if key in self.__slots__:
            setattr(self, key, None)
        else:
            raise KeyError(f"'{key}' is not an attribute of {self.__class__.__name__}")

    @no_type_check
    def _parse_children(self, elem: XmlElementLike, mask: set[str]) -> None:
        for child in elem:
            if child.tag not in mask:
                continue
            if child.tag == "prop":
                self.props.append(Prop(elem=child))
            elif child.tag == "note":
                self.notes.append(Note(elem=child))
            elif child.tag == "tuv":
                self.tuvs.append(Tuv(elem=child))
            elif child.tag == "tu":
                self.tus.append(Tu(elem=child))
            elif child.tag == "ude":
                self.udes.append(Ude(elem=child))
            elif child.tag == "map":
                self.maps.append(Map(elem=child))


class Map(Structural):
    """
    `Map` - The ``Map`` Used to specify a user-defined character and some of
    its properties.
    """

    __slots__ = "unicode", "code", "ent", "subst"

    unicode: str
    """
    The Unicode character value of the character. Its value must be a valid
    Unicode value (including values in the Private Use areas) in hexadecimal
    format.
    """
    code: str | None
    """
    The code-point value corresponding to the unicode character. Hexadecimal
    value prefixed with "#x".
    """
    ent: str | None
    """
    The entity name of the character. Text in ASCII.
    """
    subst: str | None
    """
    Alternative string for the character. Text in ASCII.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        """
        Constructor method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        if self.unicode is None:
            raise AttributeError("Attribute 'unicode' is required for Map Elements")

        return super().to_element(force_str)


class Ude(Structural):
    """
    `User-Defined Encoding` — Used to specify a set of user-defined characters
    and/or, optionally their mapping from Unicode to the user-defined encoding.
    """

    __slots__ = "name", "base", "maps"
    name: str
    """
    Name of the element, its value is not defined by the standard,
    but tools providers should publish the values they use.
    """
    base: str | None
    """
    The encoding upon which the re-mapping of the element is based.
    Note that `base` is required if at least 1 one of the :class:`Map`
    has a value set for its ``code`` attribute.
    """
    maps: MutableSequence[Map]
    """
    An array of :class:`Map` objects represents all the custom mappings for the
    encoding.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        name: str | None = None,
        base: str | None = None,
        maps: MutableSequence[Map] | None = None,
    ) -> None:
        """Constructor"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        if self.maps is None:
            self.maps = []
            if elem is not None:
                self._parse_children(elem=elem, mask={"map"})

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        if self.name is None:
            raise AttributeError("Attribute 'name' is required for Ude Elements")

        elem = super().to_element(force_str)

        # Add maps and check if base is required, raise an error if needed
        if self.maps is not None:
            for map in self.maps:
                if map.code is not None and self.base is None:
                    raise AttributeError(
                        "Attribute 'base' is required for Ude Elements with maps"
                    )
                elem.append(map.to_element(force_str))
        return elem

    def __iter__(self) -> Generator[Map, None, None]:
        yield from self.maps


class Note(Structural):
    """
    `Note` — Used for comments.

    Contrary to the :class:`Prop`, the `Note` Element is meant only to have text.
    It serves the same purpose as a basic code comment, providing context and
    additional info to the user reagrding its parent.
    """

    __slots__ = "lang", "text", "encoding"

    text: str
    """
    The actual text of the note
    """
    lang: str | None
    """
    The locale of the text of the Note. A language code as described in the
    [RFC 3066]. Unlike the other TMX attributes, the values for xml:lang
    are not case-sensitive. For more information see the section on xml:lang
    in the XML specification, and the erratum E11 (which replaces RFC 1766
    by RFC 3066).
    """
    encoding: str | None
    """
    The original or preferred code set of the data. In case it is to be
    re-encoded in a non-Unicode code set. One of the [IANA] recommended
    "charset identifier", if possible.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        text: str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        """Constructor"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        if self.text is None:
            raise AttributeError("Attribute 'text' is required for Note Elements")

        return super().to_element(force_str)


class Prop(Structural):
    """
    `Property` - Used to define the various properties of the parent element
    (or of the document when `Prop` is used in the :class:`Header`).

    These properties are not defined by the standard. As your tool is fully
    responsible for handling the content of a `Prop` element you can use it in
    any way you wish. For example the content can be a list of instructions your
    tool can parse, not only a simple text like in :class:`Note` elements.
    """

    __slots__ = "text", "lang", "type", "encoding"

    text: str
    """
    The actual text of the note
    """
    type: str
    """
    The kind of data the element represents. By convention, values are
    preppended with "x-" such as ``type="x-domain"``
    """
    lang: str | None
    """
    The locale of the text of the prop. A language code as described in the
    [RFC 3066]. Unlike the other TMX attributes, the values for xml:lang
    are not case-sensitive. For more information see the section on xml:lang
    in the XML specification, and the erratum E11 (which replaces RFC 1766
    by RFC 3066).
    """
    encoding: str | None
    """
    The original or preferred code set of the data. In case it is to be
    re-encoded in a non-Unicode code set. One of the [IANA] recommended
    "charset identifier", if possible.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        text: str | None = None,
        type: str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        """Constructor"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        if self.text is None:
            raise AttributeError("Attribute 'text' is required for Note Elements")
        if self.type is None:
            raise AttributeError("Attribute 'type' is required for Note Elements")

        return super().to_element(force_str)


class Header(Structural):
    """
    `File header` — Contains information pertaining to the whole document.
    """

    creationtool: str
    """
    The tool that created the TMX document.
    Its possible values are not specified by the standard but
    each tool provider should publish the string identifier it uses.
    """
    creationtoolversion: str
    """
    The version of the tool that created the TMX document.
    Its possible values are not specified by the standard but each tool
    provider should publish the string identifier it uses.
    """
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    """
    The default kind of segmentation used throughout the document.
    If a :class:`Tu` does not have a segtype attribute specified,
    it uses the one defined in the `Header` element.
    The "block" value is used when the segment does not correspond
    to one of the other values.
    A TMX file can include sentence level segmentation for
    maximum portability, so it is recommended that you use such
    segmentation rather than a specific, proprietary method.
    The rules on how the text was segmented can be carried in a
    Segmentation Rules eXchange (SRX) document.
    One of "block", "paragraph", "sentence", or "phrase".
    """
    tmf: str
    """
    The format of the translation memory file from which the TMX
    document or segment thereof have been generated.
    """
    adminlang: str
    """
    The default language for the administrative and informative elements
    :class:`Note` and :class:`Prop`.
    A language code as described in the [RFC 3066].
    Unlike the other TMX attributes, the values for adminlang
    are not case-sensitive.
    """
    srclang: str
    """
    The language of the source text.
    In other words, the :class:`Tuv` holding the source segment
    will have its `xml:lang` attribute set to the same value as srclang.
    If a :class:`Tu` element does not have a srclang attribute specified,
    it uses the one defined in the :class:`Header` element.
    """
    datatype: str
    """
    The type of data contained in the element.
    Depending on that type, you may apply different processes to the data.
    """
    encoding: str | None
    """
    The original or preferred code set of the data.
    In case it is to be re-encoded in a non-Unicode code set.
    One of the [IANA] recommended "charset identifier", if possible.
    """
    creationdate: datetime | None
    """The date of creation of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time."""
    creationid: str | None
    """
    The identifier of the user who created the element
    """
    changedate: datetime | None
    """
    The date of the last modification of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time.
    """
    changeid: str | None
    """
    The identifier of the user who modified the element last.
    """
    notes: MutableSequence[Note]
    """
    An array of :class:`Note` objects
    """
    props: MutableSequence[Prop]
    """
    An array of :class:`Prop` objects
    """
    udes: MutableSequence[Ude]
    """
    An array of :class:`Ude` objects
    """

    __slots__ = (
        "creationtool",
        "creationtoolversion",
        "segtype",
        "tmf",
        "adminlang",
        "srclang",
        "datatype",
        "encoding",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "notes",
        "props",
        "udes",
    )

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        tmf: str | None = None,
        adminlang: str | None = None,
        srclang: str | None = None,
        datatype: str | None = None,
        encoding: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
        udes: MutableSequence[Ude] | None = None,
    ) -> None:
        """
        Constructor Method
        """
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        mask: set[str] = set()
        if self.udes is None:
            self.udes = []
            mask.add("ude")
        if self.notes is None:
            self.notes = []
            mask.add("note")
        if self.props is None:
            self.props = []
            mask.add("prop")
        if len(mask) > 0 and elem is not None:
            self._parse_children(elem=elem, mask=mask)

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        for attr in (
            "creationtool",
            "creationtoolversion",
            "tmf",
            "adminlang",
            "srclang",
            "datatype",
            "encoding",
        ):
            if getattr(self, attr) is None:
                raise AttributeError(
                    f"Attribute '{attr}' is required for Header Elements"
                )
        elem = super().to_element(force_str)

        # Add children
        elem.extend(tuple(note.to_element(force_str) for note in self.notes))
        elem.extend(tuple(prop.to_element(force_str) for prop in self.props))
        elem.extend(tuple(ude.to_element(force_str) for ude in self.udes))

        return elem


class Tuv(Structural):
    """
    `Translation Unit Variant` - The `Tuv` element specifies text in a given
    :class:`Tu`
    """

    segment: MutableSequence[str | Inline] | str
    """
    The actual segment. Can be either a string, or an array of string and inline
    elements.
    """
    lang: str
    """
    The locale of the text of the prop. A language code as described in the
    [RFC 3066]. Unlike the other TMX attributes, the values for xml:lang
    are not case-sensitive. For more information see the section on xml:lang
    in the XML specification, and the erratum E11 (which replaces RFC 1766
    by RFC 3066).
    """
    encoding: str | None
    """
    The original or preferred code set of the data. In case it is to be
    re-encoded in a non-Unicode code set. One of the [IANA] recommended
    "charset identifier", if possible.
    """
    datatype: str | None
    """
    The type of data contained in the element.
    """
    usagecount: int | None
    """
    The number of times the content of the element has been accessed in the
    original TM environment
    """
    lastusagedate: str | datetime | None
    """
    The last time the content of the element was used in the original
    translation memory environment. Date in [ISO 8601] Format. The recommended
    pattern to use is:"YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time.
    """
    creationtool: str
    """
    The tool that created the TMX document.
    Its possible values are not specified by the standard but
    each tool provider should publish the string identifier it uses.
    """
    creationtoolversion: str
    """
    The version of the tool that created the TMX document.
    Its possible values are not specified by the standard but each tool
    provider should publish the string identifier it uses.
    """
    creationdate: datetime | None
    """The date of creation of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time."""
    creationid: str | None
    """
    The identifier of the user who created the element
    """
    changedate: datetime | None
    """
    The date of the last modification of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time.
    """
    changeid: str | None
    """
    The identifier of the user who modified the element last.
    """
    tmf: str
    """
    The format of the translation memory file from which the TMX
    document or segment thereof have been generated.
    """
    notes: MutableSequence[Note]
    """
    An array of :class:`Note` objects
    """
    props: MutableSequence[Prop]
    """
    An array of :class:`Prop` objects
    """

    __slots__ = (
        "segment",
        "lang",
        "encoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "changeid",
        "tmf",
        "notes",
        "props",
    )

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        segment: MutableSequence[str | Inline] | str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
    ) -> None:
        """Constructor Method"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        if self.segment is None:
            if elem is not None and elem.find("seg") is not None:
                self.segment = _parse_inline(elem.find("seg"))
            else:
                self.segment = None

        mask: set[str] = set()
        if self.notes is None:
            self.notes = []
            mask.add("note")
        if self.props is None:
            self.props = []
            mask.add("prop")
        if len(mask) > 0 and elem is not None:
            self._parse_children(elem=elem, mask=mask)

    def __iter__(self) -> Generator[str | Inline, None, None]:
        yield from self.segment

    def to_element(self, force_str: bool = False) -> _Element:
        # Check required attributes
        if self.lang is None:
            raise ValueError("Attribute 'lang' is required for Header Elements")
        if self.segment is None:
            raise ValueError("Attribute 'segment' is required for Header Elements")
        _check_seg(self.segment)
        elem = super().to_element(force_str)

        # Create <seg>
        if elem.find("seg") is None:
            seg = SubElement(elem, "seg")
            seg.text = ""
            last_elem: _Element | None = None
            for item in self.segment:
                if isinstance(item, Inline):
                    seg.append(item.to_element(force_str))
                    last_elem = seg[-1]
                else:
                    if last_elem is not None:
                        if last_elem.tail is None:
                            last_elem.tail = item
                        else:
                            last_elem.tail += item
                    else:
                        seg.text += item

        # Add children
        elem.extend(tuple(note.to_element(force_str) for note in self.notes))
        elem.extend(tuple(prop.to_element(force_str) for prop in self.props))
        return elem


class Tu(Structural):
    """
    `Translation unit` - The `Tu` element contains the data for a given
    translation unit.
    """

    __slots__ = (
        "tuvs",
        "tuid",
        "encoding",
        "datatype",
        "usagecount",
        "lastusagedate",
        "creationtool",
        "creationtoolversion",
        "creationdate",
        "creationid",
        "changedate",
        "segtype",
        "changeid",
        "tmf",
        "srclang",
        "notes",
        "props",
    )
    tuvs: MutableSequence[Tuv]
    """
    An array of :class:`Note` objects
    """
    tuid: str | None
    """
    An identifier for the element. Its value is not defined by the standard
    (it could be unique or not, numeric or alphanumeric, etc.).
    Text without white spaces.
    """
    encoding: str | None
    """
    The original or preferred code set of the data. In case it is to be
    re-encoded in a non-Unicode code set. One of the [IANA] recommended
    "charset identifier", if possible.
    """
    datatype: str | None
    """
    The type of data contained in the element.
    """
    usagecount: int | None
    """
    The number of times the content of the element has been accessed in the
    original TM environment
    """
    lastusagedate: str | datetime | None
    """
    The last time the content of the element was used in the original
    translation memory environment. Date in [ISO 8601] Format. The recommended
    pattern to use is:"YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time.
    """
    creationtool: str | None
    """
    The tool that created the TMX document.
    Its possible values are not specified by the standard but
    each tool provider should publish the string identifier it uses.
    """
    creationtoolversion: str | None
    """
    The version of the tool that created the TMX document.
    Its possible values are not specified by the standard but each tool
    provider should publish the string identifier it uses.
    """
    creationdate: datetime | None
    """The date of creation of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time."""
    creationid: str | None
    """
    The identifier of the user who created the element
    """
    changedate: datetime | None
    """
    The date of the last modification of the element.
    Date in [ISO 8601] Format. The recommended pattern to use is:
    "YYYYMMDDThhmmssZ" where YYYY is the year (4 digits),
    MM is the month (2 digits), DD is the day (2 digits),
    hh is the hours (2 digits), mm is the minutes (2 digits),
    ss is the second (2 digits), and Z indicates the time is UTC time.
    """
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None
    """
    The default kind of segmentation used throughout the document.
    If a :class:`Tu` does not have a segtype attribute specified,
    it uses the one defined in the `Header` element.
    The "block" value is used when the segment does not correspond
    to one of the other values.
    A TMX file can include sentence level segmentation for
    maximum portability, so it is recommended that you use such
    segmentation rather than a specific, proprietary method.
    The rules on how the text was segmented can be carried in a
    Segmentation Rules eXchange (SRX) document.
    One of "block", "paragraph", "sentence", or "phrase".
    """
    changeid: str | None
    """
    The identifier of the user who modified the element last.
    """
    tmf: str | None
    """
    The format of the translation memory file from which the TMX
    document or segment thereof have been generated.
    """
    srclang: str | None
    """
    The language of the source text.
    In other words, the :class:`Tuv` holding the source segment
    will have its `xml:lang` attribute set to the same value as srclang.
    If a :class:`Tu` element does not have a srclang attribute specified,
    it uses the one defined in the :class:`Header` element.
    """
    notes: MutableSequence[Note]
    """
    An array of :class:`Note` objects
    """
    props: MutableSequence[Prop]
    """
    An array of :class:`Prop` objects
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        tuid: str | None = None,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: str | datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        srclang: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
        tuvs: MutableSequence[Tuv] | None = None,
    ) -> None:
        """Constructor Method"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        mask: set[str] = set()
        if self.tuvs is None:
            self.tuvs = []
            mask.add("tuv")
        if self.notes is None:
            self.notes = []
            mask.add("note")
        if self.props is None:
            self.props = []
            mask.add("prop")
        if len(mask) > 0 and elem is not None:
            self._parse_children(elem=elem, mask=mask)

    def __iter__(self) -> Generator[Tuv, None, None]:
        yield from self.tuvs

    def to_element(self, force_str: bool = False) -> _Element:
        elem = super().to_element(force_str)

        # Add children
        elem.extend(tuple(note.to_element(force_str) for note in self.notes))
        elem.extend(tuple(prop.to_element(force_str) for prop in self.props))
        elem.extend(tuple(tuv.to_element(force_str) for tuv in self.tuvs))

        return elem


class Tmx(Structural):
    """
    `TMX document` - The `Tmx` element encloses all the other elements of
    the document.
    """

    __slots__ = "header", "tus"

    header: Header
    """
    A :class:`Header` element. Contains information pertaining to the whole
    document.
    """
    tus: MutableSequence[Tu]
    """
    An array of :class:`Tu` elements. Contains all the :class:`Tu` of the
    document.
    """

    def __init__(
        self,
        elem: XmlElementLike | None = None,
        strict: bool = True,
        *,
        header: Header | None = None,
        tus: MutableSequence[Tu] | None = None,
    ) -> None:
        """Constructor method"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        mask: set[str] = set()
        if self.tus is None:
            self.tus = []
            mask.add("tu")
        if len(mask) > 0 and elem is not None:
            self._parse_children(elem=elem.find("body"), mask=mask)

    def __iter__(self) -> Generator[Tu, None, None]:
        yield from self.tus

    def to_element(self, force_str: bool = False) -> _Element:
        elem = Element("tmx")
        elem.set("version", "1.4")
        elem.append(self.header.to_element(force_str))
        body = SubElement(elem, "body")
        body.extend(tuple(tu.to_element(force_str) for tu in self.tus))
        return elem
