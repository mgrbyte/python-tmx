from lxml.etree import Element, SubElement, _Element

from .core import Header, InlineElement, Note, Prop, Sub, Tmx, Tu, Tuv, Ude, Ut
from .errors import MissingSegmentError


def note_to_element(note: Note) -> _Element:
    elem = Element("note", note.model_dump(by_alias=True, exclude_none=True))
    elem.text = note.text
    return elem


def prop_to_element(prop: Prop) -> _Element:
    elem = Element("prop", prop.model_dump(by_alias=True, exclude_none=True))
    elem.text = prop.text
    return elem


def ude_to_element(ude: Ude) -> _Element:
    elem = Element("ude", ude.model_dump(by_alias=True, exclude_none=True))
    if ude.maps:
        elem.extend(
            tuple(
                Element("map", map_.model_dump(by_alias=True, exclude_none=True))
                for map_ in ude.maps
            )
        )
    return elem


def header_to_element(header: Header) -> _Element:
    header_elem = Element("header", header.model_dump(by_alias=True, exclude_none=True))
    if header.notes:
        header_elem.extend(tuple(note_to_element(note) for note in header.notes))
    if header.props:
        header_elem.extend(tuple(prop_to_element * (prop) for prop in header.props))
    if header.udes:
        header_elem.extend(tuple(ude_to_element(ude) for ude in header.udes))
    return header_elem


def inline_to_element(obj: Ut | Sub | InlineElement) -> _Element:
    elem = Element(obj.__class__.__name__.lower(), obj.model_dump(exclude_none=True))
    elem.text, elem.tail = "", ""
    parent = None
    for item in obj.content:
        if isinstance(item, (Ut, Sub, InlineElement)):
            elem.append(inline_to_element(item))
            parent = elem[-1]
        elif isinstance(item, str):
            if parent is not None:
                parent.tail = item
            else:
                elem.text += item
        else:
            raise TypeError(
                f"'{type(item).__call__.__name__}' objects are not allowed as children of '{obj.__class__.__name__}' objects"
            )
    return elem


def tuv_to_element(tuv: Tuv) -> _Element:
    tuv_elem = Element("tuv", tuv.model_dump(by_alias=True, exclude_none=True))
    if len(tuv.notes):
        tuv_elem.extend(tuple(note_to_element(note) for note in tuv.notes))
    if len(tuv.props):
        tuv_elem.extend(tuple(prop_to_element * (prop) for prop in tuv.props))
    if not len(tuv.segment):
        raise MissingSegmentError()
    seg_elem = SubElement(tuv_elem, "seg")
    seg_elem.text, seg_elem.tail = "", ""
    parent = None
    for item in tuv.segment:
        if isinstance(item, (Ut, Sub, InlineElement)):
            seg_elem.append(inline_to_element(item))
            parent = seg_elem[-1]
        elif isinstance(item, str):
            if parent is not None:
                parent.tail = item
            else:
                seg_elem.text += item
        else:
            raise TypeError(
                f"'{type(item).__call__.__name__}' objects are not allowed as children of Segment objects"
            )
    return tuv_elem


def tu_to_element(tu: Tu) -> _Element:
    tu_elem = Element("tu", tu.model_dump(exclude_none=True, by_alias=True))
    if len(tu.notes):
        tu_elem.extend(tuple(note_to_element(note) for note in tu.notes))
    if len(tu.props):
        tu_elem.extend(tuple(prop_to_element * (prop) for prop in tu.props))
    if len(tu.tuvs):
        tu_elem.extend(tuple(tuv_to_element(tuv) for tuv in tu.tuvs))
    return tu_elem


def tmx_to_element(tmx: Tmx) -> _Element:
    tmx_elem = Element("tmx", version="1.4")
    tmx_elem.append(header_to_element(tmx.header))
    body_elem = SubElement(tmx_elem, "body")
    body_elem.extend(tuple(tu_to_element(tu) for tu in tmx.tus))
    return tmx_elem
