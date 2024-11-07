from datetime import datetime
from typing import Any, Literal, MutableSequence, Protocol, Self, override

from inline import Bpt, Ept, Hi, It, Ph, Sub, Ut, _parse_inline
from lxml.etree import Element, SubElement

_empty_elem_ = Element("empty")


class XmlElementLike(Protocol):
    """
    Protocol for all ``elem`` attributes used in PythonTmx. Any class that
    follows this protocol can be used as replacement for an lxml ``_Element``
    in the context of this library.
    """

    tag: str
    text: str | None
    tail: str | None

    def get(self, key: str, default: Any) -> Any: ...
    def __iter__(self) -> Self: ...
    def __len__(self) -> int: ...


class Structural:
    """
    Base class for Structural elements.
    Not meant to be instantiated.
    """

    _source_elem: XmlElementLike | None

    def __init__(self):
        raise NotImplementedError

    def to_element(self):
        raise NotImplementedError


class Map(Structural):
    unicode: str
    code: str | None
    ent: str | None
    subst: str | None

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        unicode: str | None = None,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

        # Required Attributes
        self.unicode = unicode if unicode is not None else elem.get("unicode")

        # Optional Attributes
        self.code = code if code is not None else elem.get("code")
        self.ent = ent if ent is not None else elem.get("ent")
        self.subst = subst if subst is not None else elem.get("subst")

    @override
    def to_element(self):
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


class Ude:
    name: str
    base: str | None
    maps: MutableSequence[Map]

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        name: str | None = None,
        base: str | None | None = None,
        maps: MutableSequence[Map] | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

        # Required Attributes
        self.name = name if name is not None else elem.get("name")

        # Optional Attributes
        self.base = base if base is not None else elem.get("base")

        # Sequence Attributes
        if maps is None:
            if len(elem):
                self.maps = [
                    Map(elem=direct_child)
                    for direct_child in elem
                    if direct_child.tag == "map"
                ]
            else:
                self.maps = []
        else:
            self.maps = maps

    @override
    def to_element(self):
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


class Note:
    text: str
    lang: str | None
    encoding: str | None

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        text: str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

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


class Prop:
    text: str
    type: str
    lang: str | None
    encoding: str | None

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        text: str | None = None,
        type: str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

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
        elem = Element("prop")

        # Required Attributes
        if self.text is None:
            raise AttributeError("Attribute 'text' is required for Prop Elements")
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


class Header:
    creationtool: str
    creationtoolversion: str
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    tmf: str
    adminlang: str
    srclang: str
    datatype: str
    encoding: str | None
    creationdate: datetime | None
    creationid: str | None
    changedate: datetime | None
    changeid: str | None
    notes: MutableSequence[Note]
    props: MutableSequence[Prop]
    udes: MutableSequence[Ude]

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        tmf: str | None = None,
        adminlang: str | None = None,
        srclang: str | None = None,
        datatype: str | None = None,
        encoding: str | None | None = None,
        creationdate: datetime | None | None = None,
        creationid: str | None | None = None,
        changedate: datetime | None | None = None,
        changeid: str | None | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
        udes: MutableSequence[Ude] | None = None,
    ) -> None:
        """Constructor method"""
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

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
        if udes is None:
            if len(elem):
                self.udes = [
                    Ude(elem=direct_child)
                    for direct_child in elem
                    if direct_child.tag == "ude"
                ]
            else:
                self.udes = []
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
            raise AttributeError(
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


class Tuv:
    segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] | str
    lang: str
    encoding: str | None
    datatype: str | None
    usagecount: int | None
    lastusagedate: datetime | None
    creationtool: str | None
    creationtoolversion: str | None
    creationdate: datetime | None
    creationid: str | None
    changedate: datetime | None
    changeid: str | None
    tmf: str | None
    notes: MutableSequence[Note]
    props: MutableSequence[Prop]

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut]
        | str
        | None = None,
        lang: str | None = None,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | None = None,
        creationid: str | None = None,
        changedate: datetime | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

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

    @override
    def to_element(self):
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


class Tu:
    tuvs: MutableSequence[Tuv]
    tuid: str | None
    encoding: str | None
    datatype: str | None
    usagecount: int | None
    lastusagedate: datetime | None
    creationtool: str | None
    creationtoolversion: str | None
    creationdate: datetime | None
    creationid: str | None
    changedate: datetime | None
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None
    changeid: str | None
    tmf: str | None
    srclang: str | None
    notes: MutableSequence[Note] | None
    props: MutableSequence[Prop] | None

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        tuid: str | None = None,
        lang: str | None = None,
        encoding: str | None = None,
        datatype: str | None = None,
        usagecount: int | None = None,
        lastusagedate: datetime | None = None,
        creationtool: str | None = None,
        creationtoolversion: str | None = None,
        creationdate: datetime | None = None,
        creationid: str | None = None,
        changedate: datetime | None = None,
        segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
        changeid: str | None = None,
        tmf: str | None = None,
        srclang: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
        tuvs: MutableSequence[Tuv] | None = None,
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None

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


class Tmx:
    header: Header
    tus: MutableSequence[Tu]

    def __init__(
        self,
        *,
        elem: XmlElementLike | None = None,
        header: Header,
        tus: MutableSequence[Tu],
    ) -> None:
        elem = elem if elem is not None else _empty_elem_
        self._source_elem = elem if elem is not _empty_elem_ else None
        self.header = header if header is not None else Header(elem=elem.find("header"))
        if tus is None:
            if (body := elem.find("body")) is not None and len(body):
                self.tus.extend(Tu(elem=tu) for tu in body if tu.tag == "tu")

    def to_element(self) -> XmlElementLike:
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
