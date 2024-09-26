from lxml.etree import Element, SubElement, _Element

from .core import Header, Inline, Note, Prop, Sub, Tmx, Tu, Tuv, Ude, Ut
from .errors import MissingSegmentError


def export_note(note: Note) -> _Element:
    elem = Element("note", note.model_dump(by_alias=True, exclude_none=True))
    elem.text = note.text
    return elem


def export_prop(prop: Prop) -> _Element:
    elem = Element("prop", prop.model_dump(by_alias=True, exclude_none=True))
    elem.text = prop.text
    return elem


def export_ude(ude: Ude) -> _Element:
    elem = Element("ude", ude.model_dump(by_alias=True, exclude_none=True))
    elem.extend(
        Element("map", map_.model_dump(by_alias=True, exclude_none=True))
        for map_ in ude.maps
    )
    return elem


def export_header(header: Header) -> _Element:
    header_elem = Element("header", header.model_dump(by_alias=True, exclude_none=True))
    if len(header.notes):
        header_elem.extend(export_note(note) for note in header.notes)
    if len(header.props):
        header_elem.extend(export_prop(prop) for prop in header.props)
    if len(header.udes):
        header_elem.extend(export_ude(ude) for ude in header.udes)
    return header_elem


def export_inline(obj: Ut | Sub | Inline) -> _Element:
    elem = Element(
        obj.__class__.__name__.lower(), obj.model_dump_json(exclude_none=True)
    )
    elem.text, elem.tail = "", ""
    parent = None
    for item in obj.content:
        if isinstance(item, (Ut, Sub, Inline)):
            elem.append(export_inline(item))
            parent = elem[-1]
        elif isinstance(item, str):
            if parent:
                parent.tail = item
            else:
                elem.text += item
        else:
            raise TypeError(
                f"'{type(item).__call__.__name__}' objects are not allowed as children of '{obj.__class__.__name__}' objects"
            )
    return elem


def export_tuv(tuv: Tuv) -> _Element:
    tuv_elem = Element("tuv", tuv.model_dump(by_alias=True, exclude_none=True))
    if len(tuv.notes):
        tuv_elem.extend(export_note(note) for note in tuv.notes)
    if len(tuv.props):
        tuv_elem.extend(export_prop(prop) for prop in tuv.props)
    if not len(tuv.segment):
        raise MissingSegmentError()
    seg_elem = SubElement(tuv_elem, "seg")
    seg_elem.text, seg_elem.tail = "", ""
    parent = None
    for item in tuv.segment:
        if isinstance(item, (Ut, Sub, Inline)):
            seg_elem.append(export_inline(item))
            parent = seg_elem[-1]
        elif isinstance(item, str):
            if parent:
                parent.tail = item
            else:
                seg_elem.text += item
        else:
            raise TypeError(
                f"'{type(item).__call__.__name__}' objects are not allowed as children of Segment objects"
            )
    return tuv_elem


def export_tu(tu: Tu) -> _Element:
    tu_elem = Element("tu", tu.model_dump(exclude_none=True, by_alias=True))
    if len(tu.notes):
        tu_elem.extend(export_note(note) for note in tu.notes)
    if len(tu.props):
        tu_elem.extend(export_prop(prop) for prop in tu.props)
    if len(tu.tuvs):
        tu_elem.extend(export_tuv(tuv) for tuv in tu.tuvs)
    return tu_elem


def export_tmx(tmx: Tmx) -> _Element:
    tmx_elem = Element("tmx", version="1.4")
    tmx_elem.append(export_header(tmx.header))
    body_elem = SubElement(tmx_elem, "body")
    body_elem.extend(export_tu(tu) for tu in tmx.tus)
    return tmx_elem
