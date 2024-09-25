from lxml.etree import _Element

__XML__ = "{http://www.w3.org/XML/1998/namespace}"


def parse_element(elem: _Element) -> Note | Prop:
    match elem.tag:
        case "note":
            return Note(
                text=elem.text,
                lang=elem.get(f"{__XML__}lang"),
                encoding=elem.get("o-encoding"),
            )
        case "prop":
            return Prop(
                text=elem.text,
                type=elem.get("type"),
                lang=elem.get(f"{__XML__}lang"),
                encoding=elem.get("o-encoding"),
            )
