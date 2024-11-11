from datetime import datetime
from typing import Literal, MutableSequence, override

from lxml.etree import Element, SubElement, _Element

from PythonTmx.inline import Bpt, Ept, Hi, It, Ph, Sub, Ut, _parse_inline
from PythonTmx.utils import XmlElementLike

_Empty_Elem_ = Element("empty")


class Structural:
    """
    Base class for Structural elements. Not meant to be instantiated and purely here
    for inheritance.
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
        unicode: str = None,
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
                f"trying to create, expected 'map' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.unicode = unicode if unicode is not None else elem.get("unicode")

        # Optional Attributes
        self.code = code if code is not None else elem.get("code")
        self.ent = ent if ent is not None else elem.get("ent")
        self.subst = subst if subst is not None else elem.get("subst")

    @override
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
        *,
        elem: XmlElementLike | None = None,
        name: str = None,
        base: str | None = None,
        maps: MutableSequence[Map] | None = None,
    ) -> None:
        """Constructor"""
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "ude":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'ude' but got {elem.tag}"
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
                for map in elem:
                    if map.tag != "map":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <map> elements are allowed in a <ude> "
                            f"but got {elem.tag}"
                        )
                    self.maps.append(Map(elem=map))
        else:
            self.maps = maps

    @override
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
        if not self.base:
            if len(self.maps):
                for map in self.maps:
                    if not isinstance(map.code, str):
                        raise AttributeError(
                            "Attribute 'base' is required for Ude Elements if "
                            "they contain 1 or more Map Elements with a 'code' "
                            "attribute"
                        )
                    elem.append(map.to_element())
        else:
            elem.extend(map.to_element() for map in self.maps)
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
        *,
        elem: XmlElementLike | None = None,
        text: str = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        """Constructor"""
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "note":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'note' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.text = text if text is not None else elem.text

        # Optional Attributes
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

    @override
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
        *,
        elem: XmlElementLike | None = None,
        text: str = None,
        type: str = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        """Constructor"""
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "prop":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'prop' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.type = type if type is not None else elem.get("type")
        self.text = text if text is not None else elem.text

        # Optional Attributes
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

    @override
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
        *,
        elem: XmlElementLike | None = None,
        creationtool: str = None,
        creationtoolversion: str = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] = None,
        tmf: str = None,
        adminlang: str = None,
        srclang: str = None,
        datatype: str = None,
        encoding: str | None = None,
        creationdate: str | datetime | None = None,
        creationid: str | None = None,
        changedate: str | datetime | None = None,
        changeid: str | None = None,
        notes: MutableSequence[Note] = None,
        props: MutableSequence[Prop] = None,
        udes: MutableSequence[Ude] = None,
    ) -> None:
        """
        Constructor Method
        """
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "header":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'header' but got {elem.tag}"
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
        self.segtype = segtype if segtype is not None else elem.get("segtype")
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")
        self.adminlang = adminlang if adminlang is not None else elem.get("adminlang")
        self.srclang = srclang if srclang is not None else elem.get("srclang")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")

        # Optional Attributes
        self.creationdate = (
            creationdate if creationdate is not None else elem.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else elem.get("changedate")
        )
        self.changeid = changeid if changeid is not None else elem.get("changeid")

        # Sequence Attributes
        if notes is None:
            self.notes = []
            if len(elem):
                for note in elem:
                    if note.tag != "note":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <note>, <prop> and <ude> elements are"
                            f"allowed in a <header> but got {elem.tag}"
                        )
                    self.notes.append(Note(elem=note))
        else:
            self.notes = notes
        if props is None:
            self.props = []
            if len(elem):
                for ude in elem:
                    if ude.tag != "prop":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <note>, <prop> and <ude> elements are"
                            f"allowed in a <header> but got {elem.tag}"
                        )
                    self.props.append(Prop(elem=note))
        else:
            self.props = props
        if udes is None:
            self.udes = []
            if len(elem):
                for ude in elem:
                    if ude.tag != "ude":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <note>, <prop> and <ude> elements are"
                            f"allowed in a <header> but got {elem.tag}"
                        )
                    self.udes.append(Ude(elem=note))
        else:
            self.udes = udes

        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass

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
        if self.creationtool is None:
            raise AttributeError(
                "Attribute 'creationtool' is required for Header Elements"
            )
        elem.set("creationtool", self.creationtool)
        if self.creationtoolversion is None:
            raise AttributeError(
                "Attribute 'creationtoolversion' is required for Header Elements"
            )
        elem.set("creationtoolversion", self.creationtoolversion)
        if self.segtype is None:
            raise AttributeError("Attribute 'segtype' is required for Header Elements")
        elif self.segtype.lower() not in ("block", "paragraph", "sentence", "phrase"):
            raise ValueError(
                "Attribute 'segtype' must be one of"
                '"block", "paragraph", "sentence", "phrase"'
                f"but got {self.segtype.lower()}"
            )
        elem.set("segtype", self.segtype.lower())
        if self.tmf is None:
            raise AttributeError("Attribute 'tmf' is required for Header Elements")
        elem.set("o-tmf", self.tmf)
        if self.adminlang is None:
            raise AttributeError(
                "Attribute 'adminlang' is required for Header Elements"
            )
        elem.set("adminlang", self.adminlang)
        if self.srclang is None:
            raise AttributeError("Attribute 'srclang' is required for Header Elements")
        elem.set("srclang", self.srclang)
        if self.datatype is None:
            raise AttributeError("Attribute 'datatype' is required for Header Elements")
        elem.set("datatype", self.datatype)

        # Optional Attributes
        if self.encoding is not None:
            elem.set("o-encoding", self.encoding)
        if self.creationdate is not None:
            if isinstance(self.creationdate, datetime):
                elem.set("creationdate", self.creationdate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("creationdate", self.creationdate)
        if self.creationid is not None:
            elem.set("creationid", self.creationid)
        if self.changedate is not None:
            if isinstance(self.changedate, datetime):
                elem.set("changedate", self.changedate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("changedate", self.changedate)
        if self.changeid is not None:
            elem.set("changeid", self.changeid)

        # Sequence Attributes
        if len(self.notes):
            elem.extend(note.to_element() for note in self.notes)
        if len(self.props):
            elem.extend(prop.to_element() for prop in self.props)
        if len(self.udes):
            elem.extend(ude.to_element() for ude in self.udes)
        return elem


class Tuv(Structural):
    """
    `Translation Unit Variant` - The `Tuv` element specifies text in a given
    :class:`Tu`
    """

    segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] | str
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
        *,
        elem: XmlElementLike | None = None,
        segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut]
        | str = None,
        lang: str = None,
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
        if elem is not _Empty_Elem_ and elem.tag != "tuv":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'tuv' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # Required Attributes
        self.segment = segment if segment is None else _parse_inline(elem)

        # Optional Attributes
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.usagecount = (
            usagecount if usagecount is not None else elem.get("usagecount")
        )
        self.lastusagedate = (
            lastusagedate if lastusagedate is not None else elem.get("lastusagedate")
        )
        self.creationtool = (
            creationtool if creationtool is not None else elem.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else elem.get("creationtoolversion")
        )
        self.creationdate = (
            creationdate if creationdate is not None else elem.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else elem.get("changedate")
        )
        self.changeid = changeid if changeid is not None else elem.get("changeid")
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")

        # Try to coerce
        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass
        try:
            self.lastusagedate = datetime.strptime(
                self.lastusagedate, r"%Y%m%dT%H%M%SZ"
            )
        except (TypeError, ValueError):
            pass
        try:
            self.usagecount = int(self.usagecount)
        except (TypeError, ValueError):
            pass

        # Sequence Attributes
        if notes is None:
            self.notes = []
            if len(elem):
                for note in elem:
                    if note.tag != "note":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <note> and <prop> elements are"
                            f"allowed in a <tuv> but got {elem.tag}"
                        )
                    self.notes.append(Note(elem=note))
        else:
            self.notes = notes
        if props is None:
            self.props = []
            if len(elem):
                for ude in elem:
                    if ude.tag != "prop":
                        raise ValueError(
                            "provided element contain disallowed elements. "
                            "Only <note> and <prop> elements are"
                            f"allowed in a <tuv> but got {elem.tag}"
                        )
                    self.props.append(Prop(elem=note))
        else:
            self.props = props

    @override
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
        if len(self.notes):
            elem.extend(note.to_element() for note in self.notes)
        if len(self.props):
            elem.extend(prop.to_element() for prop in self.props)

        # Required Attributes
        if self.segment is None:
            raise AttributeError("Attribute 'segment' is required for Tuv Elements")
        seg = Element("seg")
        if isinstance(self.segment, str):
            seg.text = self.segment
        else:
            for item in self.segment:
                if isinstance(item, str):
                    if not len(seg):
                        seg[-1].tail = (
                            seg[-1].tail + item if seg[-1].tail is not None else item
                        )
                    else:
                        seg.text = seg.text + item if seg.text is not None else item
                else:
                    seg.append(item.to_element())

        # Check well-formedness of <seg> element
        bpt, ept, all_i = 0, 0, []
        for child in seg.iter("bpt", "ept"):
            if child.tag == "bpt":
                bpt += 1
                if (i := child.get("i")) not in all_i:
                    all_i.add(i)
                else:
                    raise ValueError(
                        "All 'i' attributes must be unique inside a single segment"
                    )
            else:
                ept += 1
        if bpt > ept:
            raise ValueError(
                "Every Bpt must have a corresponding Ept element but at least 1 Bpt element is orhpaned"
            )
        elif ept > bpt:
            raise ValueError(
                "Every Bpt must have a corresponding Ept element but at least 1 Ept element is orhpaned"
            )
        elem.append(seg)

        # Optional Attributes
        if self.lang is not None:
            elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.datatype is not None:
            elem.set("datatype", self.datatype)
        if self.usagecount is not None:
            if isinstance(self.usagecount, int):
                elem.set("usagecount", str(self.usagecount))
            else:
                elem.set("usagecount", self.usagecount)
        if self.lastusagedate is not None:
            if isinstance(self.lastusagedate, datetime):
                elem.set(
                    "lastusagedate", self.lastusagedate.strftime(r"%Y%m%dT%H%M%SZ")
                )
            else:
                elem.set("lastusagedate", self.lastusagedate)
        if self.creationtool is not None:
            elem.set("creationtool", self.creationtool)
        if self.creationtoolversion is not None:
            elem.set("creationtoolversion", self.creationtoolversion)
        if self.creationdate is not None:
            if isinstance(self.creationdate, datetime):
                elem.set("creationdate", self.creationdate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("creationdate", self.creationdate)
        if self.creationid is not None:
            elem.set("creationid", self.creationid)
        if self.changedate is not None:
            if isinstance(self.changedate, datetime):
                elem.set("changedate", self.changedate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("changedate", self.changedate)
        if self.changeid is not None:
            elem.set("changeid", self.changeid)
        if self.tmf is not None:
            elem.set("o-tmf", self.tmf)
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
        *,
        elem: XmlElementLike | None = None,
        tuid: str | None = None,
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
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        srclang: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
        tuvs: MutableSequence[Tuv] | None = None,
    ) -> None:
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "tu":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'tu' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None

        # No Required Attributes

        # Optional Attributes
        self.tuid = tuid if tuid is not None else elem.get("tuid")
        self.lang = (
            lang
            if lang is not None
            else elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.encoding = encoding if encoding is not None else elem.get("o-encoding")
        self.datatype = datatype if datatype is not None else elem.get("datatype")
        self.usagecount = (
            usagecount if usagecount is not None else elem.get("usagecount")
        )
        self.lastusagedate = (
            lastusagedate if lastusagedate is not None else elem.get("lastusagedate")
        )
        self.creationtool = (
            creationtool if creationtool is not None else elem.get("creationtool")
        )
        self.creationtoolversion = (
            creationtoolversion
            if creationtoolversion is not None
            else elem.get("creationtoolversion")
        )
        self.creationdate = (
            creationdate if creationdate is not None else elem.get("creationdate")
        )
        self.creationid = (
            creationid if creationid is not None else elem.get("creationid")
        )
        self.changedate = (
            changedate if changedate is not None else elem.get("changedate")
        )
        self.segtype = segtype if segtype is not None else elem.get("segtype")
        self.changeid = changeid if changeid is not None else elem.get("changeid")
        self.tmf = tmf if tmf is not None else elem.get("o-tmf")
        self.srclang = srclang if srclang is not None else elem.get("srclang")

        # Try to coerce
        try:
            self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass
        try:
            self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
        except (TypeError, ValueError):
            pass
        try:
            self.lastusagedate = datetime.strptime(
                self.lastusagedate, r"%Y%m%dT%H%M%SZ"
            )
        except (TypeError, ValueError):
            pass
        try:
            self.usagecount = int(self.usagecount)
        except (TypeError, ValueError):
            pass

        # Sequence Attributes
        if notes is None:
            if len(elem):
                self.notes = [
                    Note(elem=direct_child)
                    for direct_child in elem
                    if direct_child.tag == "note"
                ]
            else:
                self.notes = []
        else:
            self.notes = notes
        if props is None:
            if len(elem):
                self.props = [
                    Prop(elem=direct_child)
                    for direct_child in elem
                    if direct_child.tag == "prop"
                ]
            else:
                self.props = []
        else:
            self.props = props
        if tuvs is None:
            if len(elem):
                self.tuvs = [
                    Tuv(elem=direct_child)
                    for direct_child in elem
                    if direct_child.tag == "tuv"
                ]
            else:
                self.tuvs = []
        else:
            self.tuvs = tuvs

    @override
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
        elem = Element("tu")

        # Sequence Attributes
        if len(self.notes):
            elem.extend(note.to_element() for note in self.notes)
        if len(self.props):
            elem.extend(prop.to_element() for prop in self.props)

        # Required Attributes
        if self.tuvs is None:
            raise AttributeError("Attribute 'tuvs' is required for Tu Elements")
        if len(self.tuvs):
            elem.extend(tuv.to_element() for tuv in self.tuvs)

        # Optional Attributes
        if self.tuid is not None:
            elem.set("tuid", self.tuid)
        if self.lang is not None:
            elem.set("{http://www.w3.org/XML/1998/namespace}lang", self.lang)
        if self.datatype is not None:
            elem.set("datatype", self.datatype)
        if self.usagecount is not None:
            if isinstance(self.usagecount, int):
                elem.set("usagecount", str(self.usagecount))
            else:
                elem.set("usagecount", self.usagecount)
        if self.lastusagedate is not None:
            if isinstance(self.lastusagedate, datetime):
                elem.set(
                    "lastusagedate", self.lastusagedate.strftime(r"%Y%m%dT%H%M%SZ")
                )
            else:
                elem.set("lastusagedate", self.lastusagedate)
        if self.creationtool is not None:
            elem.set("creationtool", self.creationtool)
        if self.creationtoolversion is not None:
            elem.set("creationtoolversion", self.creationtoolversion)
        if self.creationdate is not None:
            if isinstance(self.creationdate, datetime):
                elem.set("creationdate", self.creationdate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("creationdate", self.creationdate)
        if self.creationid is not None:
            elem.set("creationid", self.creationid)
        if self.changedate is not None:
            if isinstance(self.changedate, datetime):
                elem.set("changedate", self.changedate.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                elem.set("changedate", self.changedate)
        if self.changeid is not None:
            elem.set("changeid", self.changeid)
        if self.segtype is not None:
            if self.segtype.lower() not in ("block", "paragraph", "sentence", "phrase"):
                raise AttributeError(
                    "Attribute 'segtype' must be one of"
                    '"block", "paragraph", "sentence", "phrase"'
                    f"but got {self.segtype.lower()}"
                )
            elem.set("segtype", self.segtype.lower())
        if self.tmf is not None:
            elem.set("o-tmf", self.tmf)
        if self.srclang is not None:
            elem.set("srclang", self.srclang)
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
        *,
        elem: XmlElementLike | None = None,
        header: Header = None,
        tus: MutableSequence[Tu] = None,
    ) -> None:
        """Constructor method"""
        elem = elem if elem is not None else _Empty_Elem_
        if elem is not _Empty_Elem_ and elem.tag != "tmx":
            raise ValueError(
                "provided element tag does not match the object you're "
                f"trying to create, expected 'tmx' but got {elem.tag}"
            )
        self._source_elem = elem if elem is not _Empty_Elem_ else None
        self.header = header if header is not None else Header(elem=elem.find("header"))
        if tus is None:
            if (body := elem.find("body")) is not None and len(body):
                self.tus.extend(Tu(elem=tu) for tu in body if tu.tag == "tu")
            else:
                self.tus = []
        else:
            self.tus = []

    def to_element(self) -> XmlElementLike:
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
        body = SubElement(elem, "body")
        if self.header is None:
            raise AttributeError(
                "The 'header' attribute of the Tmx element cannot be None"
            )
        elem.append(self.header.to_element())
        body.extend(tu.to_element() for tu in self.tus)
        return elem
