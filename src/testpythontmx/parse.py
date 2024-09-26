from __future__ import annotations

from datetime import datetime
from re import match

from lxml.etree import _Element

from .core import (
    ASSOC,
    POS,
    SEGTYPE,
    Bpt,
    Ept,
    Header,
    Hi,
    InlineElement,
    It,
    Map,
    Note,
    Ph,
    Prop,
    Sub,
    Tmx,
    Tu,
    Tuv,
    Ude,
    Ut,
)
from .errors import (
    ExtraChildrenError,
    ExtraTextError,
    MissingAttributeError,
    MissingChildrenError,
    MissingTextError,
    UnknownTagError,
)

__all__ = [
    "parse_note",
    "parse_prop",
    "parse_ude",
    "parse_map",
    "parse_header",
    "parse_inline",
    "parse_tmx",
    "parse_tu",
    "parse_tuv",
]

__XML__ = "{http://www.w3.org/XML/1998/namespace}"


def parse_note(elem: _Element) -> Note:
    if not elem.text:
        raise MissingTextError(elem.tag)
    return Note(
        text=elem.text,
        lang=elem.get(f"{__XML__}lang"),
        encoding=elem.get("o-encoding"),
    )


def parse_prop(elem: _Element) -> Prop:
    if not elem.text:
        raise MissingTextError(elem.tag)
    if not (type := elem.get("type")):
        raise MissingAttributeError("type", elem.tag)
    return Prop(
        text=elem.text,
        type=type,
        lang=elem.get(f"{__XML__}lang"),
        encoding=elem.get("o-encoding"),
    )


def parse_map(elem: _Element) -> Map:
    if not (unicode := elem.get("unicode")):
        raise MissingAttributeError("unicode", elem.tag)
    if elem.text and not match(r"\s*", elem.text):
        raise ExtraTextError(elem.tag, elem.text)
    if len(elem):
        raise ExtraChildrenError(elem.tag, elem[0].tag)
    return Map(
        unicode=unicode,
        code=elem.get("code"),
        ent=elem.get("ent"),
        subst=elem.get("subst"),
    )


def parse_ude(elem: _Element) -> Ude:
    if not (name := elem.get("name")):
        raise MissingAttributeError("name", elem.tag)
    if elem.text and not match(r"\s*", elem.text):
        raise ExtraTextError(elem.tag, elem.text)
    if not len(elem):
        raise MissingChildrenError(elem.tag)
    return Ude(
        name=name,
        base=elem.get("base"),
        maps=[parse_map(child) for child in elem.iterchildren("map")],
    )


def parse_header(elem: _Element) -> Header:
    if not (creationtool := elem.get("creationtool")):
        raise MissingAttributeError("creationtool", elem.tag)
    if not (creationtoolversion := elem.get("creationtoolversion")):
        raise MissingAttributeError("creationtoolversion", elem.tag)
    if not (segtype := elem.get("segtype")):
        raise MissingAttributeError("segtype", elem.tag)
    if not (tmf := elem.get("o-tmf")):
        raise MissingAttributeError("o-tmf", elem.tag)
    if not (adminlang := elem.get("adminlang")):
        raise MissingAttributeError("adminlang", elem.tag)
    if not (srclang := elem.get("srclang")):
        raise MissingAttributeError("srclang", elem.tag)
    if not (datatype := elem.get("datatype")):
        raise MissingAttributeError("datatype", elem.tag)
    header = Header(
        creationtool=creationtool,
        creationtoolversion=creationtoolversion,
        segtype=SEGTYPE(segtype),
        tmf=tmf,
        adminlang=adminlang,
        srclang=srclang,
        datatype=datatype,
        encoding=elem.get("o-encoding"),
        creationid=elem.get("creationid"),
        changeid=elem.get("changeid"),
        notes=[parse_note(child) for child in elem.iterchildren("note")],
        props=[parse_prop(child) for child in elem.iterchildren("prop")],
        udes=[parse_ude(child) for child in elem.iterchildren("ude")],
    )
    if creationdate := elem.get("creationdate"):
        header.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
    if changedate := elem.get("changedate"):
        header.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
    return header


def parse_inline(elem: _Element) -> InlineElement | Sub | Ut:
    def parse_ph(elem: _Element) -> Ph:
        if not (x := elem.get("x")):
            raise MissingAttributeError("x", elem.tag)
        ph = Ph(
            x=int(x),
            type=elem.get("type"),
        )
        if (assoc := elem.get("assoc")) is not None:
            ph.assoc = ASSOC(assoc)
        return ph

    def parse_bpt(elem: _Element) -> Bpt:
        if not (i := elem.get("i")):
            raise MissingAttributeError("i", elem.tag)
        x = elem.get("x")
        bpt = Bpt(
            i=int(i),
            x=int(x) if x else None,
            type=elem.get("type"),
        )
        return bpt

    def parse_ept(elem: _Element) -> Ept:
        if not (i := elem.get("i")):
            raise MissingAttributeError("i", elem.tag)
        ept = Ept(i=int(i))
        return ept

    def parse_hi(elem: _Element) -> Hi:
        if not (x := elem.get("x")):
            raise MissingAttributeError("x", elem.tag)
        hi = Hi(
            x=int(x),
            type=elem.get("type"),
        )
        return hi

    def parse_it(elem: _Element) -> It:
        if not (pos := elem.get("pos")):
            raise MissingAttributeError("pos", elem.tag)
        x = elem.get("x")
        it = It(
            pos=POS(pos),
            x=int(x) if x else None,
            type=elem.get("type"),
        )
        return it

    def parse_sub(elem: _Element) -> Sub:
        sub = Sub(
            datatype=elem.get("datatype"),
            type=elem.get("type"),
        )
        return sub

    def parse_ut(elem: _Element) -> Ut:
        x = elem.get("x")
        ut = Ut(
            x=int(x) if x else None,
        )
        return ut

    inline: InlineElement | Sub | Ut
    match elem.tag:
        case "ph":
            inline = parse_ph(elem)
        case "bpt":
            inline = parse_bpt(elem)
        case "ept":
            inline = parse_ept(elem)
        case "hi":
            inline = parse_hi(elem)
        case "it":
            inline = parse_it(elem)
        case "sub":
            inline = parse_sub(elem)
        case "ut":
            inline = parse_ut(elem)
        case _:
            raise UnknownTagError(elem.tag)
    if elem.text and not match(r"\s*", elem.text):
        inline.content.append(elem.text)
    if len(elem):
        for child in elem:
            inline.content.append(parse_inline(child))  # type: ignore
            if child.tail:
                inline.content.append(child.tail)
    return inline


def parse_tuv(elem: _Element) -> Tuv:
    if not (lang := elem.get(f"{__XML__}lang")):
        raise MissingAttributeError("lang", elem.tag)
    tuv = Tuv(
        lang=lang,
        encoding=elem.get("o-encoding"),
        datatype=elem.get("datatype"),
        creationtool=elem.get("creationtool"),
        creationtoolversion=elem.get("creationtoolversion"),
        creationid=elem.get("creationid"),
        changeid=elem.get("changeid"),
        tmf=elem.get("o-tmf"),
        notes=[parse_note(child) for child in elem.iterchildren("note")],
        props=[parse_prop(child) for child in elem.iterchildren("prop")],
    )
    seg = elem.find("seg")
    if seg is None:
        raise ValueError("Tuv is missing seg element")
    if seg.text is not None:
        tuv.segment.append(seg.text)
    if len(seg) > 1:
        for child in seg:
            tuv.segment.append(parse_inline(child))  # type:ignore
            if child.tail is not None:
                tuv.segment.append(child.tail)
    if creationdate := elem.get("creationdate"):
        tuv.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
    if changedate := elem.get("changedate"):
        tuv.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
    if lastusagedate := elem.get("lastusagedate"):
        tuv.lastusagedate = datetime.strptime(lastusagedate, r"%Y%m%dT%H%M%SZ")
    if usagecount := elem.get("usagecount"):
        tuv.usagecount = int(usagecount)
    return tuv


def parse_tu(elem: _Element) -> Tu:
    tu = Tu(
        tuid=elem.get("tuid"),
        encoding=elem.get("o-encoding"),
        datatype=elem.get("datatype"),
        creationtool=elem.get("creationtool"),
        creationtoolversion=elem.get("creationtoolversion"),
        creationid=elem.get("creationid"),
        changeid=elem.get("changeid"),
        tmf=elem.get("o-tmf"),
        srclang=elem.get("srclang"),
        notes=[parse_note(child) for child in elem.iterchildren("note")],
        props=[parse_prop(child) for child in elem.iterchildren("prop")],
        tuvs=[parse_tuv(child) for child in elem.iterchildren("tuv")],
    )
    if creationdate := elem.get("creationdate"):
        tu.creationdate = datetime.strptime(creationdate, r"%Y%m%dT%H%M%SZ")
    if changedate := elem.get("changedate"):
        tu.changedate = datetime.strptime(changedate, r"%Y%m%dT%H%M%SZ")
    if lastusagedate := elem.get("lastusagedate"):
        tu.lastusagedate = datetime.strptime(lastusagedate, r"%Y%m%dT%H%M%SZ")
    if usagecount := elem.get("usagecount"):
        tu.usagecount = int(usagecount)
    if segtype := elem.get("segtype"):
        tu.segtype = SEGTYPE(segtype)
    return tu


def parse_tmx(elem: _Element) -> Tmx:
    if (head_elem := elem.find("header")) is not None:
        header = parse_header(head_elem)
    tus = [parse_tu(child) for child in elem.iter("tu")]
    tmx = Tmx(header=header, tus=tus)
    return tmx
