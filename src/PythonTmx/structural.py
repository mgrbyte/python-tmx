"""
This module contains all the structural elements of a tmx file.
They are the building blocks of a tmx file.
"""

from collections.abc import MutableSequence
from datetime import datetime
from logging import warning
from typing import Literal

from lxml.etree import Element, SubElement, _Element

from PythonTmx import XmlElementLike, _Empty_Elem_
from PythonTmx.inline import Inline, _parse_inline


class Structural:
    """
    Base class for Structural elements. Doesn't contain any logic and is only
    here for inheritance.
    """

    __slots__ = ("_source_elem",)

    _source_elem: XmlElementLike | None

    def __init__(self):
        raise NotImplementedError

    def to_element(self) -> _Element:
        raise NotImplementedError


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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "map":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected <map> but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.unicode = unicode if unicode is not None else elem.get("unicode")

        # Optional Attributes
        self.code = code if code is not None else elem.get("code")
        self.ent = ent if ent is not None else elem.get("ent")
        self.subst = subst if subst is not None else elem.get("subst")

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
        if self.code is not None:
            elem.set("code", self.code)
        if self.ent is not None:
            elem.set("ent", self.ent)
        if self.subst is not None:
            elem.set("subst", self.subst)
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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "ude":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected <ude> but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.name = name if name is not None else elem.get("name")

        # Optional Attributes
        self.base = base if base is not None else elem.get("base")

        # Sequence Attributes
        if maps is None:
            self.maps = []
            if len(elem):
                self.maps.extend(Map(elem=map) for map in elem)
        else:
            self.maps = maps

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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "note":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected <note> but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.text = (
            text if text is not None else elem.text if elem.text is not None else ""
        )

        # Optional Attributes
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "prop":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected <prop> but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.type = type if type is not None else elem.get("type")
        self.text = (
            text if text is not None else elem.text if elem.text is not None else ""
        )

        # Optional Attributes
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "header":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected <header> but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.creationtool = (
            creationtool if creationtool is not None else elem.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else elem.get("creationtoolversion")
        )
        # special logic for segtype to check the actual value
        if segtype is None:
            # We're type checking right below so we can ignore mypy
            segtype = elem.get("segtype")  # type: ignore
        if segtype is not None:
            if segtype in ("block", "paragraph", "sentence", "phrase"):
                self.segtype = segtype
            else:
                warning(
                    "Attribute 'segtype' must be one of "
                    '"block", "paragraph", "sentence", "phrase"'
                    f"but got {segtype.lower()}"
                )
                # forcing mypy to ignore since we already warned the user
                self.segtype = segtype  # type: ignore
        else:
            warning(
                "Attribute 'segtype' must be one of "
                '"block", "paragraph", "sentence", "phrase"'
            )
            self.segtype = None  # type: ignore
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")
        self.adminlang = adminlang if adminlang is not None else elem.get("adminlang")
        self.srclang = srclang if srclang is not None else elem.get("srclang")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

        # Optional Attributes

        # datetime attributes
        if creationdate is None:
            creationdate = elem.get("creationdate")
        if isinstance(creationdate, datetime):
            self.creationdate = creationdate
        else:
            try:
                self.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
            except (ValueError, TypeError):
                warning(f"Could not parse creationdate '{creationdate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.creationdate = creationdate  # type: ignore
            except Exception as e:
                raise e
        if changedate is None:
            changedate = elem.get("changedate")
        if isinstance(changedate, datetime):
            self.changedate = changedate
        else:
            try:
                self.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(f"Could not parse changedate '{changedate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.changedate = changedate  # type: ignore
            except Exception as e:
                raise e
        # other attributes
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        self.changeid = changeid if changeid is not None else elem.get("changeid")

        # Sequence Attributes
        # mask is used to check if we need to grab them from the element or not
        # to grab avoid iterating the element three times at worst
        mask: list[str] = []
        if notes is None:
            self.notes = []
            mask.append("notes")
        if props is None:
            self.props = []
            mask.append("props")
        if udes is None:
            self.udes = []
            mask.append("udes")
        if elem is not None:
            for child in elem:
                if child.tag == "note" and "notes" in mask:
                    self.notes.append(Note(elem=child))
                elif child.tag == "prop" and "props" in mask:
                    self.props.append(Prop(elem=child))
                elif child.tag == "ude" and "udes" in mask:
                    self.udes.append(Ude(elem=child))
                else:
                    warning(
                        "provided element contain disallowed elements. "
                        "Only <note>, <prop> and <ude> elements are"
                        f"allowed in a <header> but got {elem.tag}"
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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_:
            if elem.tag != "tuv":
                raise ValueError(
                    "provided element tag does not match the object you're "
                    f"trying to create, expected <tuv> but got {elem.tag}"
                )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        if segment is None and elem is not _Empty_Elem_:
            if (seg := elem.find("seg")) is None:
                raise ValueError(
                    "provided <tuv> element does not contain a <seg> element"
                )
            else:
                self.segment = _parse_inline(seg)
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )

        # Optional Attributes
        # str attributes
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.changeid = changeid if changeid is not None else elem.get("changeid")
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")

        # int attributes
        if usagecount is None:
            # We're type checking right below so we can ignore mypy
            usagecount = elem.get("usagecount")  # type: ignore
        if isinstance(usagecount, int):
            self.usagecount = usagecount
        else:
            try:
                # We're expecting it to potentially fail so we can ignore mypy
                self.usagecount = int(usagecount)  # type: ignore
            except (ValueError, TypeError):
                warning(f"Could not parse usagecount '{usagecount}' as an int")
                # Already warned the user above so we can ignore mypy
                self.usagecount = usagecount  # type: ignore
            except Exception as e:
                raise e

        # datetime attributes
        if lastusagedate is None:
            lastusagedate = elem.get("lastusagedate")
        if isinstance(lastusagedate, datetime):
            self.lastusagedate = lastusagedate
        else:
            try:
                self.lastusagedate = datetime.strptime(lastusagedate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(
                    f"Could not parse lastusagedate '{lastusagedate}' as a datetime"
                )
                # Already warned the user above so we can ignore mypy
                self.lastusagedate = lastusagedate  # type: ignore
            except Exception as e:
                raise e
        self.creationtool = (
            creationtool if creationtool is not None else elem.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else elem.get("creationtoolversion")
        )
        if creationdate is None:
            creationdate = elem.get("creationdate")
        if isinstance(creationdate, datetime):
            self.creationdate = creationdate
        else:
            try:
                self.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(f"Could not parse creationdate '{creationdate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.creationdate = creationdate  # type: ignore
            except Exception as e:
                raise e
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        if changedate is None:
            changedate = elem.get("changedate")
        if isinstance(changedate, datetime):
            self.changedate = changedate
        else:
            try:
                self.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(f"Could not parse changedate '{changedate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.changedate = changedate  # type: ignore
            except Exception as e:
                raise e

        # Sequence Attributes
        # mask is used to check if we need to grab them from the element or not
        # to grab avoid iterating the element three times at worst
        mask: list[str] = []
        if notes is None:
            self.notes = []
            mask.append("notes")
        if props is None:
            self.props = []
            mask.append("props")
        if elem is not None:
            for child in elem:
                if child.tag == "note" and "notes" in mask:
                    self.notes.append(Note(elem=child))
                elif child.tag == "prop" and "props" in mask:
                    self.props.append(Prop(elem=child))
                elif child.tag == "seg":
                    # ignore seg since we dealt with it earlier
                    pass
                else:
                    warning(
                        "provided element contain disallowed elements. "
                        "Only <note>, <prop> and elements are"
                        f"allowed in a <tuv> but got {elem.tag}"
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
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_:
            if elem.tag != "tuv":
                raise ValueError(
                    "provided element tag does not match the object you're "
                    f"trying to create, expected <tuv> but got {elem.tag}"
                )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # No Required Attributes

        # Optional Attributes
        # str attributes
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.tuid = tuid if tuid is not None else elem.get("tuid")
        self.srclang = srclang if srclang is not None else elem.get("srclang")
        self.changeid = changeid if changeid is not None else elem.get("changeid")
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else elem.get("creationtoolversion")
        )

        # special logic for segtype to check the actual value
        if segtype is None:
            # We're type checking right below so we can ignore mypy
            segtype = elem.get("segtype")  # type: ignore
        if segtype is not None:
            if segtype in ("block", "paragraph", "sentence", "phrase"):
                self.segtype = segtype
            else:
                warning(
                    "Attribute 'segtype' must be one of "
                    '"block", "paragraph", "sentence", "phrase"'
                    f"but got {segtype.lower()}"
                )
                # forcing mypy to ignore since we already warned the user
                self.segtype = segtype  # type: ignore
        else:
            warning(
                "Attribute 'segtype' must be one of "
                '"block", "paragraph", "sentence", "phrase"'
            )
            self.segtype = None  # type: ignore

        # int attributes
        if usagecount is None:
            # We're type checking right below so we can ignore mypy
            usagecount = elem.get("usagecount")  # type: ignore
        if isinstance(usagecount, int):
            self.usagecount = usagecount
        else:
            try:
                # We're expecting it to potentially fail so we can ignore mypy
                self.usagecount = int(usagecount)  # type: ignore
            except (ValueError, TypeError):
                warning(f"Could not parse usagecount '{usagecount}' as an int")
                # Already warned the user above so we can ignore mypy
                self.usagecount = usagecount  # type: ignore
            except Exception as e:
                raise e

        # datetime attributes
        if lastusagedate is None:
            lastusagedate = elem.get("lastusagedate")
        if isinstance(lastusagedate, datetime):
            self.lastusagedate = lastusagedate
        else:
            try:
                self.lastusagedate = datetime.strptime(lastusagedate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(
                    f"Could not parse lastusagedate '{lastusagedate}' as a datetime"
                )
                # Already warned the user above so we can ignore mypy
                self.lastusagedate = lastusagedate  # type: ignore
            except Exception as e:
                raise e
        self.creationtool = (
            creationtool if creationtool is not None else elem.get("creationtool")
        )

        if creationdate is None:
            creationdate = elem.get("creationdate")
        if isinstance(creationdate, datetime):
            self.creationdate = creationdate
        else:
            try:
                self.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(f"Could not parse creationdate '{creationdate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.creationdate = creationdate  # type: ignore
            except Exception as e:
                raise e
        if changedate is None:
            changedate = elem.get("changedate")
        if isinstance(changedate, datetime):
            self.changedate = changedate
        else:
            try:
                self.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
            except ValueError:
                warning(f"Could not parse changedate '{changedate}' as a datetime")
                # Already warned the user above so we can ignore mypy
                self.changedate = changedate  # type: ignore
            except Exception as e:
                raise e

        # Sequence Attributes
        # mask is used to check if we need to grab them from the element or not
        # to grab avoid iterating the element three times at worst
        mask: list[str] = []
        if notes is None:
            self.notes = []
            mask.append("notes")
        if props is None:
            self.props = []
            mask.append("props")
        if tuvs is None:
            self.tuvs = []
            mask.append("tuvs")
        if elem is not None:
            for child in elem:
                if child.tag == "note" and "notes" in mask:
                    self.notes.append(Note(elem=child))
                elif child.tag == "prop" and "props" in mask:
                    self.props.append(Prop(elem=child))
                elif child.tag == "tuv" and "tuvs" in mask:
                    self.tuvs.append(Tuv(elem=child))
                else:
                    warning(
                        "provided element contain disallowed elements. "
                        "Only <note>, <prop> and <tuv> elements are"
                        f"allowed in a <tu> but got {elem.tag}"
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
        elem = elem if elem is not None else _Empty_Elem_
        self._source_elem = elem if elem is not _Empty_Elem_ else None
        if elem is not _Empty_Elem_:
            if elem.tag != "tmx":
                raise ValueError(
                    "provided element tag does not match the object you're "
                    f"trying to create, expected <tmx> but got {elem.tag}"
                )
            if header is not None:
                self.header = header
            else:
                if (_header := elem.find("header")) is None:
                    warning(
                        "provided <tmx> element does not contain a <header> element"
                    )
                    # Already warned the user above so we can ignore mypy
                    self.header = _header  # type: ignore
                else:
                    self.header = Header(elem=_header)
            if tus is not None:
                self.tus = tus
            else:
                if (body := elem.find("body")) is None:
                    warning("provided <tmx> element does not contain a <body> element")
                    self.tus = []
                else:
                    self.tus = []
                    self.tus.extend(Tu(elem=tu) for tu in body)

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
