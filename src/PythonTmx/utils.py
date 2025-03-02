import itertools
from collections.abc import MutableSequence
from dataclasses import MISSING, fields
from datetime import datetime

from lxml.etree import Element, _Element

from PythonTmx.classes import (
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
  TmxElement,
  Tu,
  Tuv,
  Ude,
  Ut,
)

__all__ = ["to_element", "from_element"]

xml = r"{http://www.w3.org/XML/1998/namespace}"


def _make_attrib_dict(map_: TmxElement, keep_extra: bool) -> dict[str, str]:
  attrib_dict: dict[str, str] = dict()
  for attr in fields(map_):
    if attr.metadata.get("exclude", False):
      continue
    name, value, func = (
      attr.metadata.get("export_name", attr.name),
      getattr(map_, attr.name),
      attr.metadata.get("export_func", str),
    )
    if value is None:
      if attr.default is MISSING:
        raise ValueError(f"missing attribute {attr.name}")
    else:
      attrib_dict[name] = func(value) if func else value
  if keep_extra:
    attrib_dict.update(**map_.extra)
  return attrib_dict


def _fill_inline_content(
  content: MutableSequence, /, element: _Element, keep_extra: bool
) -> None:
  parent = None
  for item in content:
    if isinstance(item, InlineElement):
      parent = to_element(item, keep_extra=keep_extra)
      element.append(parent)
    else:
      if parent is None:
        if element.text is None:
          element.text = item
        else:
          element.text += item
      else:
        if parent.tail is None:
          parent.tail = item
        else:
          parent.tail += item


def _parse_inline_content(element: _Element, /, keep_extra: bool) -> MutableSequence:
  content: MutableSequence = []
  if element.text is not None:
    content.append(element.text)
  for child in element:
    match child.tag:
      case "bpt":
        content.append(_parse_bpt(child, keep_extra=keep_extra))
      case "ept":
        content.append(_parse_ept(child, keep_extra=keep_extra))
      case "it":
        content.append(_parse_it(child, keep_extra=keep_extra))
      case "ph":
        content.append(_parse_ph(child, keep_extra=keep_extra))
      case "hi":
        content.append(_parse_hi(child, keep_extra=keep_extra))
      case "ut":
        content.append(_parse_ut(child, keep_extra=keep_extra))
      case "sub":
        content.append(_parse_sub(child, keep_extra=keep_extra))
      case _:
        raise ValueError(f"Unknown element {child.tag!r}")
    if child.tail is not None:
      content.append(child.tail)
  return content


def _parse_bpt(element: _Element, /, keep_extra: bool) -> Bpt:
  return Bpt(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
    x=element.attrib.pop("x", None),
    type=element.attrib.pop("type", None),
  )


def _parse_ept(element: _Element, /, keep_extra: bool) -> Ept:
  return Ept(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
  )


def _parse_it(element: _Element, /, keep_extra: bool) -> It:
  return It(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    pos=POS(element.attrib.pop("pos")),
    x=element.attrib.pop("x", None),
    type=element.attrib.pop("type", None),
  )


def _parse_ph(element: _Element, /, keep_extra: bool) -> Ph:
  return Ph(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    x=element.attrib.pop("x", None),
    assoc=ASSOC(element.attrib.pop("assoc", None)),
    type=element.attrib.pop("type", None),
  )


def _parse_hi(element: _Element, /, keep_extra: bool) -> Hi:
  return Hi(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    x=element.attrib.pop("x", None),
    type=element.attrib.pop("type", None),
  )


def _parse_ut(element: _Element, /, keep_extra: bool) -> Ut:
  return Ut(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    x=element.attrib.pop("x", None),
  )


def _parse_sub(element: _Element, /, keep_extra: bool) -> Sub:
  return Sub(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    datatype=element.attrib.pop("datatype", None),
    type=element.attrib.pop("type", None),
  )


def _parse_map(element: _Element, /, keep_extra: bool = False) -> Map:
  return Map(
    unicode=element.attrib.pop("unicode"),
    code=element.attrib.pop("code", None),
    ent=element.attrib.pop("ent", None),
    subst=element.attrib.pop("subst", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_ude(element: _Element, /, keep_extra: bool = False) -> Ude:
  ude = Ude(
    name=element.attrib.pop("name"),
    base=element.attrib.get("base", None),
    extra=dict(element.attrib) if keep_extra else {},
    maps=[_parse_map(child, keep_extra=keep_extra) for child in element.iter("map")],
  )
  return ude


def _parse_note(element: _Element, /, keep_extra: bool = False) -> Note:
  return Note(
    # Intentionally passing .text as is to let dataclasses handle the type error
    text=element.text,  # type: ignore
    lang=element.attrib.pop(f"{xml}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_prop(element: _Element, /, keep_extra: bool = False) -> Prop:
  return Prop(
    # Intentionally passing .text as is to let dataclasses handle the type error
    text=element.text,  # type: ignore
    type=element.attrib.pop("type"),
    lang=element.attrib.pop(f"{xml}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_header(element: _Element, /, keep_extra: bool = False) -> Header:
  header = Header(
    creationtool=element.attrib.pop("creationtool"),
    creationtoolversion=element.attrib.pop("creationtoolversion"),
    segtype=SEGTYPE(element.attrib.pop("segtype")),
    tmf=element.attrib.pop("o-tmf"),
    adminlang=element.attrib.pop("adminlang"),
    srclang=element.attrib.pop("srclang"),
    datatype=element.attrib.pop("datatype"),
    encoding=element.attrib.pop("o-encoding", None),
    creationid=element.attrib.pop("creationid", None),
    changeid=element.attrib.pop("changeid", None),
    notes=[_parse_note(child, keep_extra=keep_extra) for child in element.iter("note")],
    props=[_parse_prop(child, keep_extra=keep_extra) for child in element.iter("prop")],
    udes=[_parse_ude(child, keep_extra=keep_extra) for child in element.iter("ude")],
  )
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    header.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    header.changedate = datetime.fromisoformat(changedate)
  if keep_extra:
    header.extra = dict(element.attrib)
  return header


def _parse_tuv(element: _Element, /, keep_extra: bool = False) -> Tuv:
  tuv = Tuv(
    lang=element.attrib.pop(f"{xml}lang"),
    encoding=element.attrib.pop("o-encoding", None),
    datatype=element.attrib.pop("datatype", None),
    creationtool=element.attrib.pop("creationtool", None),
    creationtoolversion=element.attrib.pop("creationtoolversion", None),
    creationid=element.attrib.pop("creationid", None),
    tmf=element.attrib.pop("o-tmf", None),
    changeid=element.attrib.pop("changeid", None),
    props=[
      _parse_prop(child, keep_extra=keep_extra) for child in element.findall("prop")
    ],
    notes=[
      _parse_note(child, keep_extra=keep_extra) for child in element.findall("note")
    ],
  )
  if (seg := element.find("seg")) is not None:
    tuv.content = _parse_inline_content(seg, keep_extra=keep_extra)
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    tuv.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    tuv.changedate = datetime.fromisoformat(changedate)
  if (lastusagedate := element.attrib.pop("lastusagedate", None)) is not None:
    tuv.changedate = datetime.fromisoformat(lastusagedate)
  if (usagecount := element.attrib.pop("usagecount", None)) is not None:
    tuv.usagecount = int(usagecount)
  if keep_extra:
    tuv.extra = dict(element.attrib)
  return tuv


def _parse_tu(element: _Element, /, keep_extra: bool = False) -> Tu:
  tu = Tu(
    tuid=element.attrib.pop("tuid", None),
    encoding=element.attrib.pop("o-encoding", None),
    datatype=element.attrib.pop("datatype", None),
    creationtool=element.attrib.pop("creationtool", None),
    creationtoolversion=element.attrib.pop("creationtoolversion", None),
    creationid=element.attrib.pop("creationid", None),
    changeid=element.attrib.pop("changeid", None),
    tmf=element.attrib.pop("o-tmf", None),
    srclang=element.attrib.pop("srclang", None),
    notes=[
      _parse_note(child, keep_extra=keep_extra) for child in element.findall("note")
    ],
    props=[
      _parse_prop(child, keep_extra=keep_extra) for child in element.findall("prop")
    ],
    tuvs=[_parse_tuv(child, keep_extra=keep_extra) for child in element.findall("tuv")],
  )
  if lastusagedate := element.attrib.pop("lastusagedate", None):
    tu.lastusagedate = datetime.fromisoformat(lastusagedate)
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    tu.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    tu.changedate = datetime.fromisoformat(changedate)
  if (segtype := element.attrib.pop("segtype", None)) is not None:
    tu.segtype = SEGTYPE(segtype)
  if (usagecount := element.attrib.pop("usagecount", None)) is not None:
    tu.usagecount = int(usagecount)
  if keep_extra:
    tu.extra = dict(element.attrib)
  return tu


def _parse_tmx(element: _Element, /, keep_extra: bool = False) -> Tmx:
  return Tmx(
    header=_parse_header(element.find("header"), keep_extra=keep_extra),  # type: ignore
    tus=[_parse_tu(child, keep_extra=keep_extra) for child in element.iter("tu")],
    extra=dict(element.attrib) if keep_extra else {},
  )


def from_element(element: _Element, /, keep_extra: bool = False) -> TmxElement:
  match element.tag:
    case "map":
      return _parse_map(element, keep_extra=keep_extra)
    case "ude":
      return _parse_ude(element, keep_extra=keep_extra)
    case "note":
      return _parse_note(element, keep_extra=keep_extra)
    case "prop":
      return _parse_prop(element, keep_extra=keep_extra)
    case "header":
      return _parse_header(element, keep_extra=keep_extra)
    case "tuv":
      return _parse_tuv(element, keep_extra=keep_extra)
    case "tu":
      return _parse_tu(element, keep_extra=keep_extra)
    case "tmx":
      return _parse_tmx(element, keep_extra=keep_extra)
    case "bpt":
      return _parse_bpt(element, keep_extra=keep_extra)
    case "ept":
      return _parse_ept(element, keep_extra=keep_extra)
    case "it":
      return _parse_it(element, keep_extra=keep_extra)
    case "ph":
      return _parse_ph(element, keep_extra=keep_extra)
    case "hi":
      return _parse_hi(element, keep_extra=keep_extra)
    case "ut":
      return _parse_ut(element, keep_extra=keep_extra)
    case "sub":
      return _parse_sub(element, keep_extra=keep_extra)
    case _:
      raise ValueError(f"Unknown element {element.tag!r}")


def _map_to_element(map_: Map, /, keep_extra: bool = False) -> _Element:
  elem = Element("map")
  elem.attrib.update(_make_attrib_dict(map_, keep_extra=keep_extra))
  return elem


def _ude_to_element(ude: Ude, /, keep_extra: bool = False) -> _Element:
  elem = Element("ude")
  elem.attrib.update(_make_attrib_dict(ude, keep_extra=keep_extra))
  elem.extend([_map_to_element(map_, keep_extra=keep_extra) for map_ in ude.maps])
  return elem


def _note_to_element(note: Note, /, keep_extra: bool = False) -> _Element:
  elem = Element("note")
  elem.text = note.text
  elem.attrib.update(_make_attrib_dict(note, keep_extra=keep_extra))
  return elem


def _prop_to_element(prop: Prop, /, keep_extra: bool = False) -> _Element:
  elem = Element("prop")
  elem.text = prop.text
  elem.attrib.update(_make_attrib_dict(prop, keep_extra=keep_extra))
  return elem


def _header_to_element(header: Header, /, keep_extra: bool = False) -> _Element:
  elem = Element("header")
  elem.attrib.update(_make_attrib_dict(header, keep_extra=keep_extra))
  elem.extend(
    [
      to_element(item, keep_extra=keep_extra)
      for item in itertools.chain(header.notes, header.props, header.udes)
    ]
  )
  return elem


def _tuv_to_element(tuv: Tuv, /, keep_extra: bool = False) -> _Element:
  elem = Element("tuv")
  elem.attrib.update(_make_attrib_dict(tuv, keep_extra=keep_extra))
  elem.extend(
    [
      to_element(item, keep_extra=keep_extra)
      for item in itertools.chain(tuv.notes, tuv.props)
    ]
  )
  seg = Element("seg")
  elem.append(seg)
  _fill_inline_content(tuv.content, seg, keep_extra=keep_extra)
  return elem


def _tu_to_element(tu: Tu, /, keep_extra: bool = False) -> _Element:
  elem = Element("tu")
  elem.attrib.update(_make_attrib_dict(tu, keep_extra=keep_extra))
  elem.extend(
    [
      to_element(item, keep_extra=keep_extra)
      for item in itertools.chain(tu.notes, tu.props, tu.tuvs)
    ]
  )
  return elem


def _tmx_to_element(tmx: Tmx, /, keep_extra: bool = False) -> _Element:
  elem = Element("tmx", version="1.4")
  body = Element("body")
  elem.append(_header_to_element(tmx.header, keep_extra=keep_extra))
  elem.append(body)
  body.extend([to_element(item, keep_extra=keep_extra) for item in tmx.tus])
  return elem


def _ph_to_element(ph: Ph, /, keep_extra: bool = False) -> _Element:
  elem = Element("ph")
  elem.attrib.update(_make_attrib_dict(ph, keep_extra=keep_extra))
  _fill_inline_content(ph.content, elem, keep_extra=keep_extra)
  return elem


def _bpt_to_element(bpt: Bpt, /, keep_extra: bool = False) -> _Element:
  elem = Element("bpt")
  elem.attrib.update(_make_attrib_dict(bpt, keep_extra=keep_extra))
  _fill_inline_content(bpt.content, elem, keep_extra=keep_extra)
  return elem


def _ept_to_element(ept: Ept, /, keep_extra: bool = False) -> _Element:
  elem = Element("ept")
  elem.attrib.update(_make_attrib_dict(ept, keep_extra=keep_extra))
  _fill_inline_content(ept.content, elem, keep_extra=keep_extra)
  return elem


def _it_to_element(it: It, /, keep_extra: bool = False) -> _Element:
  elem = Element("it")
  elem.attrib.update(_make_attrib_dict(it, keep_extra=keep_extra))
  _fill_inline_content(it.content, elem, keep_extra=keep_extra)
  return elem


def _ut_to_element(ut: Ut, /, keep_extra: bool = False) -> _Element:
  elem = Element("ut")
  elem.attrib.update(_make_attrib_dict(ut, keep_extra=keep_extra))
  _fill_inline_content(ut.content, elem, keep_extra=keep_extra)
  return elem


def _sub_to_element(sub: Sub, /, keep_extra: bool = False) -> _Element:
  elem = Element("sub")
  elem.attrib.update(_make_attrib_dict(sub, keep_extra=keep_extra))
  _fill_inline_content(sub.content, elem, keep_extra=keep_extra)
  return elem


def _hi_to_element(hi: Hi, /, keep_extra: bool = False) -> _Element:
  elem = Element("hi")
  elem.attrib.update(_make_attrib_dict(hi, keep_extra=keep_extra))
  _fill_inline_content(hi.content, elem, keep_extra=keep_extra)
  return elem


def to_element(element: TmxElement, /, keep_extra: bool = False) -> _Element:
  match element:
    case Map():
      return _map_to_element(element, keep_extra=keep_extra)
    case Ude():
      return _ude_to_element(element, keep_extra=keep_extra)
    case Note():
      return _note_to_element(element, keep_extra=keep_extra)
    case Prop():
      return _prop_to_element(element, keep_extra=keep_extra)
    case Header():
      return _header_to_element(element, keep_extra=keep_extra)
    case Tuv():
      return _tuv_to_element(element, keep_extra=keep_extra)
    case Tu():
      return _tu_to_element(element, keep_extra=keep_extra)
    case Tmx():
      return _tmx_to_element(element, keep_extra=keep_extra)
    case Ph():
      return _ph_to_element(element, keep_extra=keep_extra)
    case Bpt():
      return _bpt_to_element(element, keep_extra=keep_extra)
    case Ept():
      return _ept_to_element(element, keep_extra=keep_extra)
    case It():
      return _it_to_element(element, keep_extra=keep_extra)
    case Ut():
      return _ut_to_element(element, keep_extra=keep_extra)
    case Sub():
      return _sub_to_element(element, keep_extra=keep_extra)
    case Hi():
      return _hi_to_element(element, keep_extra=keep_extra)
    case _:
      raise ValueError(f"Unknown element {element}")
