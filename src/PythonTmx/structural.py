from datetime import datetime
from typing import Literal, MutableSequence, Optional, overload

from lxml.etree import Element, _Element

from .inline import Bpt, Ept, Hi, It, Ph, Sub, Ut, _parse_inline

_xml_ = "w3.org/xml/1998/namespace"
_EmptyElem_ = Element("empty")


class Map:
    unicode: str
    code: str | None
    ent: str | None
    subst: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        unicode: str,
        code: str | None = None,
        ent: str | None = None,
        subst: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...  # hack to make mypy happy

    def __init__(self, **kwargs) -> None:
        """
        Used to specify a user-defined character and some of its properties.
        Can only exist as a child of a Ude element.

        :param unicode: The Unicode character value
        :type unicode: str
        :param elem: An lxml Element to use as default for attribute values,
        defaults to None.
        :type elem: _Element | None, optional
        :param code: The code-point value of to the unicode character.
        :type code: str | None, optional
        :param ent: The entity name of the character, defaults to None
        :type ent: str | None, optional
        :param subst: An alternative string, defaults to None
        :type subst: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.unicode = kwargs.get("unicode", elem.get("unicode"))
        self.code = kwargs.get("code", elem.get("code"))
        self.ent = kwargs.get("ent", elem.get("ent"))
        self.subst = kwargs.get("subst", elem.get("subst"))


class Ude:
    name: str
    base: str | None
    maps: MutableSequence[Map] | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        name: str,
        base: str | None = None,
        maps: MutableSequence[Map] | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        Used to specify a set of user-defined characters and/or, optionally
        their mapping from Unicode to the user-defined encoding.

        :param name: Name of the element, its value is not defined by the standard
        :type name: str
        :param elem: An lxml Element to use as default for attribute values,
        defaults to None.
        :type elem: _Element | None, optional
        :param base: The encoding upon which the re-mapping is based, defaults to None.
        Required if one or more of the Map elements contains a code attribute.
        :type base: str | None, optional
        :param maps: An array of all the Map Elements consituting the Ude, defaults to None
        :type maps: MutableSequence[Map] | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        if "maps" in kwargs:
            self.maps = kwargs.get("maps")
        elif len(elem):
            self.maps = [Map(elem=child) for child in elem if child.tag == "map"]
        else:
            self.maps = []
        self.name = kwargs.get("name", elem.get("name"))
        self.base = kwargs.get("base", elem.get("base"))


class Note:
    text: str
    lang: str | None
    encoding: str | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(self, *, text: str, encoding: str | None = None) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        Used for comments.

        :param elem: An lxml Element to use as default for attribute values,
        defaults to None.
        :type elem: _Element | None, optional
        :param text: The actual text of the Note
        :type text: str
        :param lang: The locale of the text, defaults to None
        :type lang: str | None, optional
        :param encoding: The original or preferred code set of the data of the
        element in case it is to be re-encoded in a non-Unicode code set, defaults to None
        :type encoding: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.text = kwargs.get("text", elem.text)
        self.lang = kwargs.get("lang", elem.get(f"{_xml_}base"))
        self.encoding = kwargs.get("encoding", elem.get("o-encoding"))


class Prop:
    text: str
    type: str
    lang: Optional[str]
    encoding: Optional[str]

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        elem: _Element | None = None,
        text: str,
        type: str,
        encoding: str | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param elem: An lxml Element to use as default for attribute values,
        defaults to None.
        :type elem: _Element | None, optional
        :param text: The actual text of the Note
        :type text: str
        :param type: the kind of data the element represents.
        :type type: str
        :param lang: The locale of the text, defaults to None
        :type lang: str | None, optional
        :param encoding: The original or preferred code set of the data of the
        element in case it is to be re-encoded in a non-Unicode code set, defaults to None
        :type encoding: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.text = kwargs.get("text", elem.text)
        self.lang = kwargs.get("lang", elem.get(f"{_xml_}base"))
        self.encoding = kwargs.get("encoding", elem.get("o-encoding"))
        self.type = kwargs.get("type", elem.get("type"))


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
    notes: MutableSequence[Note] | None
    props: MutableSequence[Prop] | None

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        creationtool: str,
        creationtoolversion: str,
        segtype: Literal["block", "paragraph", "sentence", "phrase"],
        tmf: str,
        adminlang: str,
        srclang: str,
        datatype: str,
        encoding: str | None = None,
        creationdate: datetime | None = None,
        creationid: str | None = None,
        changedate: datetime | None = None,
        changeid: str | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param creationtool: _description_
        :type creationtool: str
        :param creationtoolversion: _description_
        :type creationtoolversion: str
        :param segtype: _description_
        :type segtype: Literal[&quot;block&quot;, &quot;paragraph&quot;, &quot;sentence&quot;, &quot;phrase&quot;]
        :param tmf: _description_
        :type tmf: str
        :param adminlang: _description_
        :type adminlang: str
        :param srclang: _description_
        :type srclang: str
        :param datatype: _description_
        :type datatype: str
        :param encoding: _description_, defaults to None
        :type encoding: str | None, optional
        :param creationdate: _description_, defaults to None
        :type creationdate: datetime | None, optional
        :param creationid: _description_, defaults to None
        :type creationid: str | None, optional
        :param changedate: _description_, defaults to None
        :type changedate: datetime | None, optional
        :param changeid: _description_, defaults to None
        :type changeid: str | None, optional
        :param notes: _description_, defaults to None
        :type notes: MutableSequence[Note] | None, optional
        :param props: _description_, defaults to None
        :type props: MutableSequence[Prop] | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.creationtool = kwargs.get("creationtool", elem.get("creationtool"))
        self.creationtoolversion = kwargs.get(
            "creationtoolversion", elem.get("creationtoolversion")
        )
        self.segtype = kwargs.get("segtype", elem.get("segtype"))
        self.tmf = kwargs.get("tmf", elem.get("o-tmf"))
        self.adminlang = kwargs.get("adminlang", elem.get("adminlang"))
        self.srclang = kwargs.get("srclang", elem.get("srclang"))
        self.datatype = kwargs.get("datatype", elem.get("datatype"))
        self.encoding = kwargs.get("encoding", elem.get("o-encoding"))
        self.creationdate = kwargs.get("creationdate", elem.get("creationdate"))
        self.creationid = kwargs.get("creationid", elem.get("creationid"))
        self.changedate = kwargs.get("changedate", elem.get("changedate"))
        self.changeid = kwargs.get("changeid", elem.get("changeid"))
        if "notes" in kwargs:
            self.notes = kwargs.get("notes")
        elif len(elem):
            self.notes = [Note(elem=child) for child in elem if child.tag == "note"]
        else:
            self.notes = []
        if "props" in kwargs:
            self.props = kwargs.get("props")
        elif len(elem):
            self.props = [Prop(elem=child) for child in elem if child.tag == "prop"]
        else:
            self.props = []
        if isinstance(self.creationdate, str):
            try:
                self.creationdate = datetime.strptime(
                    self.creationdate, r"%Y%m%dT%H%M%SZ"
                )
            except (TypeError, ValueError):
                pass
        if isinstance(self.changedate, str):
            try:
                self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
            except (TypeError, ValueError):
                pass


class Tuv:
    segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut]
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

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        segment: MutableSequence[str | Bpt | Ept | It | Hi | Ph | Sub | Ut] | str,
        lang: str,
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
        tmf: str | None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param segment: _description_
        :type segment: MutableSequence[str  |  Bpt  |  Ept  |  It  |  Hi  |  Ph  |  Sub  |  Ut] | str
        :param lang: _description_
        :type lang: str
        :param tmf: _description_
        :type tmf: str | None
        :param encoding: _description_, defaults to None
        :type encoding: str | None, optional
        :param datatype: _description_, defaults to None
        :type datatype: str | None, optional
        :param usagecount: _description_, defaults to None
        :type usagecount: int | None, optional
        :param lastusagedate: _description_, defaults to None
        :type lastusagedate: datetime | None, optional
        :param creationtool: _description_, defaults to None
        :type creationtool: str | None, optional
        :param creationtoolversion: _description_, defaults to None
        :type creationtoolversion: str | None, optional
        :param creationdate: _description_, defaults to None
        :type creationdate: datetime | None, optional
        :param creationid: _description_, defaults to None
        :type creationid: str | None, optional
        :param changedate: _description_, defaults to None
        :type changedate: datetime | None, optional
        :param changeid: _description_, defaults to None
        :type changeid: str | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.segment = kwargs.get("segment", _parse_inline(elem=elem.find("seg")))
        self.lang = kwargs.get("lang", elem.get(f"{_xml_}lang"))
        self.encoding = kwargs.get("encoding", elem.get("o-encoding"))
        self.datatype = kwargs.get("datatype", elem.get("datatype"))
        self.usagecount = kwargs.get("usagecount", elem.get("usagecount"))
        self.lastusagedate = kwargs.get("lastusagedate", elem.get("lastusagedate"))
        self.creationtool = kwargs.get("creationtool", elem.get("creationtool"))
        self.creationtoolversion = kwargs.get(
            "creationtoolversion", elem.get("creationtoolversion")
        )
        self.creationdate = kwargs.get("creationdate", elem.get("creationdate"))
        self.creationid = kwargs.get("creationid", elem.get("creationid"))
        self.changedate = kwargs.get("changedate", elem.get("changedate"))
        self.changeid = kwargs.get("changeid", elem.get("changeid"))
        self.tmf = kwargs.get("tmf", elem.get("o-tmf"))

        if isinstance(self.creationdate, str):
            try:
                self.creationdate = datetime.strptime(
                    self.creationdate, r"%Y%m%dT%H%M%SZ"
                )
            except (TypeError, ValueError):
                pass
        if isinstance(self.changedate, str):
            try:
                self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
            except (TypeError, ValueError):
                pass
        if isinstance(self.lastusagedate, str):
            try:
                self.lastusagedate = datetime.strptime(
                    self.lastusagedate, r"%Y%m%dT%H%M%SZ"
                )
            except (TypeError, ValueError):
                pass
        if isinstance(self.usagecount, str):
            try:
                self.usagecount = int(self.usagecount)
            except (TypeError, ValueError):
                pass


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

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(
        self,
        *,
        tuid: str | None = None,
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
        tuvs: MutableSequence[Tuv] | None = None,
        notes: MutableSequence[Note] | None = None,
        props: MutableSequence[Prop] | None = None,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param tuid: _description_, defaults to None
        :type tuid: str | None, optional
        :param encoding: _description_, defaults to None
        :type encoding: str | None, optional
        :param datatype: _description_, defaults to None
        :type datatype: str | None, optional
        :param usagecount: _description_, defaults to None
        :type usagecount: int | None, optional
        :param lastusagedate: _description_, defaults to None
        :type lastusagedate: datetime | None, optional
        :param creationtool: _description_, defaults to None
        :type creationtool: str | None, optional
        :param creationtoolversion: _description_, defaults to None
        :type creationtoolversion: str | None, optional
        :param creationdate: _description_, defaults to None
        :type creationdate: datetime | None, optional
        :param creationid: _description_, defaults to None
        :type creationid: str | None, optional
        :param changedate: _description_, defaults to None
        :type changedate: datetime | None, optional
        :param segtype: _description_, defaults to None
        :type segtype: Literal[&quot;block&quot;, &quot;paragraph&quot;, &quot;sentence&quot;, &quot;phrase&quot;] | None, optional
        :param changeid: _description_, defaults to None
        :type changeid: str | None, optional
        :param tmf: _description_, defaults to None
        :type tmf: str | None, optional
        :param srclang: _description_, defaults to None
        :type srclang: str | None, optional
        :param tuvs: _description_, defaults to None
        :type tuvs: MutableSequence[Tuv] | None, optional
        :param notes: _description_, defaults to None
        :type notes: MutableSequence[Note] | None, optional
        :param props: _description_, defaults to None
        :type props: MutableSequence[Prop] | None, optional
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.lang = kwargs.get("lang", elem.get(f"{_xml_}lang"))
        self.encoding = kwargs.get("encoding", elem.get("o-encoding"))
        self.datatype = kwargs.get("datatype", elem.get("datatype"))
        self.usagecount = kwargs.get("usagecount", elem.get("usagecount"))
        self.lastusagedate = kwargs.get("lastusagedate", elem.get("lastusagedate"))
        self.creationtool = kwargs.get("creationtool", elem.get("creationtool"))
        self.creationtoolversion = kwargs.get(
            "creationtoolversion", elem.get("creationtoolversion")
        )
        self.creationdate = kwargs.get("creationdate", elem.get("creationdate"))
        self.creationid = kwargs.get("creationid", elem.get("creationid"))
        self.changedate = kwargs.get("changedate", elem.get("changedate"))
        self.segtype = kwargs.get("segtype", elem.get("segtype"))
        self.changeid = kwargs.get("changeid", elem.get("changeid"))
        self.tmf = kwargs.get("tmf", elem.get("otmf"))
        self.srclang = kwargs.get("srclang", elem.get("srclang"))
        self.tuvs = kwargs.get(
            "tuvs",
            [Tuv(elem=child) for child in elem if child.tag == "tuv"],
        )
        self.notes = kwargs.get(
            "notes", [Note(elem=child) for child in elem if child.tag == "note"]
        )
        self.props = kwargs.get(
            "props", [Prop(elem=child) for child in elem if child.tag == "prop"]
        )

        if isinstance(self.creationdate, str):
            try:
                self.creationdate = datetime.strptime(
                    self.creationdate, r"%Y%m%dT%H%M%SZ"
                )
            except (TypeError, ValueError):
                pass
        if isinstance(self.changedate, str):
            try:
                self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
            except (TypeError, ValueError):
                pass
        if isinstance(self.lastusagedate, str):
            try:
                self.lastusagedate = datetime.strptime(
                    self.lastusagedate, r"%Y%m%dT%H%M%SZ"
                )
            except (TypeError, ValueError):
                pass
        if isinstance(self.usagecount, str):
            try:
                self.usagecount = int(self.usagecount)
            except (TypeError, ValueError):
                pass


class Tmx:
    header: Header
    tus: MutableSequence[Tu]

    @overload
    def __init__(self, *, elem: _Element | None = None) -> None: ...
    @overload
    def __init__(self, *, header: Header, tus: MutableSequence[Tu]) -> None: ...
    @overload
    def __init__(self, **kwargs) -> None: ...

    def __init__(self, **kwargs) -> None:
        """
        _summary_

        :param header: _description_
        :type header: Header
        :param tus: _description_
        :type tus: MutableSequence[Tu]
        """
        elem: _Element = kwargs.get("elem", _EmptyElem_)
        self.header = kwargs.get("header", Header(elem=elem.find("header")))
        if "tus" in kwargs:
            self.tus = kwargs["tus"]
        else:
            if (body := elem.find("body")) is not None:
                self.tus = [Tu(elem=child) for child in body if child.tag == "tu"]
            else:
                self.tus = []
