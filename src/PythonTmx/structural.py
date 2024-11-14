"""
This module contains all the structural elements of a tmx file.
They are the building blocks of a tmx file.
"""

# General Comment: We're intentionally letting users use the library without
# having to worry about type errors when creating a tmx object from scratch.
# Exorting to an Element though is much more strict and will raise an error if
# the user tries to do something that is not allowed.
from collections.abc import MutableSequence
from datetime import datetime
from typing import Literal, assert_never, no_type_check

from lxml.etree import Element, SubElement, _Element

from PythonTmx import XmlElementLike, _Empty_Elem_
from PythonTmx.inline import Inline, _parse_inline


class Structural:
    """
    Base class for Structural elements. DO NOT USE THIS CLASS DIRECTLY.
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

        for attr, value in kwargs.items():
            if attr in ("elem"):
                continue
            if attr in self.__slots__:
                if attr == "text":  # get text from text attribute not attrib dict
                    setattr(self, attr, value if value is not None else elem.text)
                elif attr == "header":  # create an empty header if no value
                    setattr(
                        self,
                        attr,
                        value if value is not None else Header(),
                    )
                elif attr in (
                    "creationdate",
                    "changedate",
                    "lastusagedate",
                ):  # try to coerce datetime values
                    if isinstance(value, datetime):
                        setattr(self, attr, value)
                    elif isinstance(value, str):
                        try:
                            setattr(
                                self, attr, datetime.strptime(value, "%Y%m%dT%H%M%SZ")
                            )
                        except ValueError:
                            setattr(self, attr, value)
                    else:
                        setattr(self, attr, value)
                elif attr == "lang":  # get lang from xml:lang attribute
                    self.lang = (
                        value
                        if value is not None
                        else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
                    )
                elif attr in ("encoding", "tmf"):  # get those from o-attributes
                    setattr(
                        self,
                        attr,
                        value if value is not None else elem.get(f"o-{attr}"),
                    )
                elif attr == "usagecount":  # try to coerce int values
                    try:
                        setattr(self, attr, int(value))
                    except (ValueError, TypeError):
                        setattr(self, attr, value)
                elif attr in ("notes", "props", "tus", "tuvs", "udes", "maps"):
                    setattr(self, attr, value)
                elif attr == "segment":  # parse segment if needed using parse_inline
                    setattr(
                        self,
                        attr,
                        value if value is not None else _parse_inline(elem.find("seg")),
                    )
                else:
                    setattr(self, attr, value if value is not None else elem.get(attr))
            else:
                assert_never(attr)

    def to_element(self) -> _Element:
        raise NotImplementedError

    # mypy will always complain here since it can't know that the subclasses
    # will have the props or notes attribute when this is called so we disable
    # type checking for this method
    @no_type_check
    def _parse_children(self, elem: XmlElementLike, mask: set[str]) -> None:
        for child in elem:
            if child.tag not in mask:
                continue
            if child.tag == "prop":
                self.props.append = Prop(elem=child)
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

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("map")

        # Required Attributes
        if self.unicode is None:
            raise AttributeError("Attribute 'unicode' is required for Map Elements")
        elem.set("unicode", self.unicode)

        # Optional Attributes
        for attr in ("code", "ent", "subst"):
            if getattr(self, attr) is not None:
                elem.set(attr, getattr(self, attr))
        return elem


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
            self._parse_children(
                elem=elem if elem is not None else _Empty_Elem_, mask={"map"}
            )

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.
        Will recursively call :func:`Map.to_element()` on all the :class:`Map`
        elements and append them to the main Ude element before returning.

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
        """
        elem = Element("ude")

        # Required Attributes
        if self.name is None:
            raise AttributeError("Attribute 'name' is required for Ude Elements")
        elem.set("name", self.name)

        # Optional Attributes/Sequence Attributes
        if self.base is None:
            if len(self.maps):
                for map in self.maps:
                    if map.code is not None:
                        raise AttributeError(
                            "Attribute 'base' is required for Ude Elements if "
                            "at least 1 or more Map Elements have a 'code'"
                            " attribute"
                        )
                    elem.append(map.to_element())
        else:
            elem.extend(map.to_element() for map in self.maps)
            elem.set("base", self.base)
        return elem


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

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("note")

        # Required Attributes
        if self.text is None:
            raise AttributeError("Attribute 'text' is required for Note Elements")
        elem.text = self.text

        # Optional Attributes
        if self.lang is not None:
            elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)
        return elem


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

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("prop")

        # Required Attributes
        if self.text is None:
            raise AttributeError("Attribute 'content' is required for Prop Elements")
        elem.text = self.text
        if self.type is None:
            raise AttributeError("Attribute 'type' is required for Prop Elements")
        elem.set("type", self.type)

        # Optional Attributes
        if self.lang is not None:
            elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)
        return elem


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
        mask = set()
        if self.udes is None:
            self.udes = []
            mask.add("ude")
        if self.notes is None:
            self.notes = []
            mask.add("note")
        if self.props is None:
            self.props = []
            mask.add("prop")
        if len(mask) > 0:
            self._parse_children(
                elem=elem if elem is not None else _Empty_Elem_,
                mask=mask,
            )

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Attribute with ``datetime`` values will be converted to a string.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        ValueError
            Raised if segtype is not one of the accepted values
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("header")

        # Required Attributes
        for attr in (
            "creationtool",
            "creationtoolversion",
            "adminlang",
            "srclang",
            "datatype",
        ):
            if getattr(self, attr) is None:
                raise AttributeError(
                    f"Attribute '{attr}' is required for Header Elements"
                )
            elem.set(attr, getattr(self, attr))
        if self.segtype is None:
            raise AttributeError("Attribute 'segtype' is required for Header Elements")
        elif self.segtype not in ("block", "paragraph", "sentence", "phrase"):
            raise ValueError(
                "Attribute 'segtype' must be one of"
                '"block", "paragraph", "sentence", "phrase"'
                f"but got {self.segtype}"
            )
        else:
            elem.set("segtype", self.segtype)
        if self.tmf is None:
            raise AttributeError("Attribute 'tmf' is required for Header Elements")
        elem.set("o-tmf", self.tmf)

        # Optional Attributes
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)
        for attr in ("creationdate", "changedate"):
            if (val := getattr(self, attr)) is not None:
                if isinstance(val, datetime):
                    elem.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                elif isinstance(val, str):
                    try:
                        elem.set(
                            attr,
                            datetime.strptime(val, r"%Y%m%dT%H%M%SZ").strftime(
                                r"%Y%m%dT%H%M%SZ"
                            ),
                        )
                    except ValueError as e:
                        raise ValueError(
                            f"Invalid valid for '{attr}'. {val} does not follow"
                            " the YYYYMMDDTHHMMSS format"
                        ) from e
            elem.set("creationid", self.creationid)
        if self.changeid is not None:
            elem.set("changeid", self.changeid)

        # Sequence Attributes
        elem.extend(note.to_element() for note in self.notes)
        elem.extend(prop.to_element() for prop in self.props)
        elem.extend(ude.to_element() for ude in self.udes)
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
        self._parse_children(
            elem=elem if elem is not None else _Empty_Elem_, mask={"prop", "note"}
        )

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Attribute with ``datetime`` values will be converted to a string.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        ValueError
            Raised if :attr:`segtype` is not one of the accepted values,
            if 2 or more `Bpt` elements have the same 'i' attribute or if there
            is an orphaned `Bpt` or `Ept` element
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("tuv")

        # Sequence Attributes
        # Need to have these first to follow the DTD
        elem.extend(note.to_element() for note in self.notes)
        elem.extend(prop.to_element() for prop in self.props)

        # Required Attributes
        if self.lang is not None:
            elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)

        # Segment logic
        if self.segment is None:
            raise AttributeError("Attribute 'segment' is required for Tuv Elements")
        seg = SubElement(elem, "seg")
        if isinstance(self.segment, str):
            seg.text = self.segment
        else:
            for item in self.segment:
                if isinstance(item, str):
                    # If seg has already has another inline, add or append
                    # the text as the tail of that element
                    if len(seg):
                        seg[-1].tail = (
                            seg[-1].tail + item if seg[-1].tail is not None else item
                        )
                    # If seg has no inline, add the text as the text of the element
                    else:
                        seg.text = seg.text + item if seg.text is not None else item
                else:
                    # else just append the element
                    seg.append(item.to_element())

        # Check bpt 'i' attributes are unique and each bpt has an ept
        bpt, ept, all_i = 0, 0, []
        for child in seg.iter("bpt", "ept"):
            if child.tag == "bpt":
                bpt += 1
                if (i := child.get("i")) not in all_i:
                    all_i.append(i)
                else:
                    raise ValueError(
                        "All 'i' attributes must be unique inside a single segment"
                    )
            else:
                ept += 1
        if bpt > ept:
            raise ValueError(
                "Every Bpt must have a corresponding Ept element but at least "
                "1 Bpt element is orhpaned"
            )
        elif ept > bpt:
            raise ValueError(
                "Every Bpt must have a corresponding Ept element but at least "
                "1 Ept element is orhpaned"
            )

        # Optional Attributes
        # str attributes
        for attr in (
            "creationtool",
            "creationtoolversion",
            "creationid",
            "datatype",
            "changeid",
        ):
            if getattr(self, attr) is not None:
                elem.set(attr, getattr(self, attr))

        if self.tmf is not None:
            elem.set("o-tmf", self.tmf)
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)

        # int attributes
        if self.usagecount is not None:
            if isinstance(self.usagecount, int):
                elem.set("usagecount", str(self.usagecount))
            else:
                elem.set("usagecount", self.usagecount)

        # datetime attributes
        for attr in ("creationdate", "changedate", "lastusagedate"):
            if (val := getattr(self, attr)) is not None:
                if isinstance(val, datetime):
                    elem.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                elif isinstance(val, str):
                    try:
                        elem.set(
                            attr,
                            datetime.strptime(val, r"%Y%m%dT%H%M%SZ"),
                        )
                    except ValueError as e:
                        raise ValueError(
                            f"Invalid valid for '{attr}'. {val} does not follow"
                            " the YYYYMMDDTHHMMSS format"
                        ) from e
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
        self._parse_children(
            elem=elem if elem is not None else _Empty_Elem_,
            mask={"tuv", "prop", "note"},
        )

    def to_element(self):
        """
        Converts the object into an lxml `_Element`, validating that all
        required attribtues are present, skipping any optional attributes with
        a value of `None` and changing the attribute name to make the resulting
        `_Element` spec-compliant.

        Attribute with ``datetime`` values will be converted to a string.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        ValueError
            Raised if :attr:`segtype` is not one of the accepted values,
            if 2 or more `Bpt` elements have the same 'i' attribute or if there
            is an orphaned `Bpt` or `Ept` element
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("tu")

        # Sequence Attributes
        # need to have note and prop first to follow DTD
        elem.extend(note.to_element() for note in self.notes)
        elem.extend(prop.to_element() for prop in self.props)
        elem.extend(tuv.to_element() for tuv in self.tuvs)

        # Required Attributes

        # Optional Attributes
        # str attributes
        for attr in (
            "creationtool",
            "creationtoolversion",
            "creationid",
            "datatype",
            "changeid",
        ):
            if getattr(self, attr) is not None:
                elem.set(attr, getattr(self, attr))

        if self.tmf is not None:
            elem.set("o-tmf", self.tmf)
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)

        # int attributes
        if self.usagecount is not None:
            if isinstance(self.usagecount, int):
                elem.set("usagecount", str(self.usagecount))
            else:
                elem.set("usagecount", self.usagecount)

        # datetime attributes
        for attr in ("creationdate", "changedate", "lastusagedate"):
            if (val := getattr(self, attr)) is not None:
                if isinstance(val, datetime):
                    elem.set(attr, val.strftime(r"%Y%m%dT%H%M%SZ"))
                elif isinstance(val, str):
                    try:
                        elem.set(
                            attr,
                            datetime.strptime(val, r"%Y%m%dT%H%M%SZ"),
                        )
                    except ValueError as e:
                        raise ValueError(
                            f"Invalid valid for '{attr}'. {val} does not follow"
                            " the YYYYMMDDTHHMMSS format"
                        ) from e
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
        *,
        header: Header | None = None,
        tus: MutableSequence[Tu] | None = None,
    ) -> None:
        """Constructor method"""
        vals = locals()
        vals.pop("self")
        vals.pop("__class__")
        super().__init__(**vals)
        self._parse_children(
            elem=elem if elem is not None else _Empty_Elem_, mask={"tu"}
        )

    def to_element(self) -> _Element:
        """
        Converts the object into an lxml `_Element`. Always sets the `version`
        attribute to "1.4b" and converts the header and all the
        :class:`Tu` to xml elements as well.

        Returns
        -------
        _Element
            A Tmx compliant lxml Element, ready to written to a file or
            manipulated however you see fit.

        Raises
        ------
        AttributeError
            Raised if a required attribute has a value of `None`
        TypeError
            Raised by lxml if trying to set a value that is not a `str`
        """
        elem = Element("tmx")
        elem.set("version", "1.4")
        if self.header is None:
            raise AttributeError(
                "The 'header' attribute of the Tmx element cannot be None"
            )
        elem.append(self.header.to_element())
        body = SubElement(elem, "body")
        body.extend([tu.to_element() for tu in self.tus])
        return elem
