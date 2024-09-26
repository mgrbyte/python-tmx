from lxml.etree import Element, _Element

from .core import Map, Note, Prop

__XML__ = "{http://www.w3.org/XML/1998/namespace}"


def export_note(note: Note) -> _Element:
    note_elem = Element(
        "note", {"o-encoding": note.encoding, f"{__XML__}lang": note.lang}
    )
    note_elem.text = note.text
    return note_elem


def export_prop(prop: Prop) -> _Element:
    prop_elem = Element(
        "prop",
        {"type": prop.type, "o-encoding": prop.encoding, f"{__XML__}lang": prop.lang},
    )
    prop_elem.text = prop.text
    return prop_elem


def export_map(map: Map) -> _Element:
    return Element(
        "map",
        **{
            key: map.__getattribute__(key)
            for key in map.__slots__
            if map.__getattribute__(key) is not None
        },
    )
