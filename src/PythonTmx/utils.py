import xml.etree.ElementTree as pyet
from collections import Counter
from collections.abc import Iterable
from dataclasses import MISSING, fields
from datetime import datetime
from functools import cache
from itertools import chain
from typing import Any, Literal, Type, get_type_hints, overload

import lxml.etree as lxet

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
    if value is not None:
      attrib_dict[name] = func(value)
  if keep_extra:
    attrib_dict.update(**map_.extra)
  return attrib_dict


def _fill_inline_content(
  content: Iterable, /, element: lxet._Element | pyet.Element, keep_extra: bool
) -> None:
  parent = None
  for item in content:
    if isinstance(item, InlineElement):
      parent = to_element(item, keep_extra=keep_extra)  # type:ignore
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


def _parse_inline_content(
  element: lxet._Element | pyet.Element, /, keep_extra: bool
) -> list:
  content: list = []
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


def _parse_bpt(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Bpt:
  bpt = Bpt(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    bpt.x = int(x)
  if keep_extra:
    bpt.extra = dict(element.attrib)
  return bpt


def _parse_ept(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ept:
  return Ept(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_it(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> It:
  it = It(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    pos=POS(element.attrib.pop("pos")),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    it.x = int(x)
  if keep_extra:
    it.extra = dict(element.attrib)
  return it


def _parse_ph(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ph:
  ph = Ph(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    assoc=ASSOC(element.attrib.pop("assoc", None)),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    ph.x = int(x)
  if keep_extra:
    ph.extra = dict(element.attrib)
  return ph


def _parse_hi(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Hi:
  hi = Hi(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    hi.x = int(x)
  if keep_extra:
    hi.extra = dict(element.attrib)
  return hi


def _parse_ut(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ut:
  ut = Ut(
    content=_parse_inline_content(element, keep_extra=keep_extra),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    ut.x = int(x)
  if keep_extra:
    ut.extra = dict(element.attrib)
  return ut


def _parse_sub(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Sub:
  return Sub(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    datatype=element.attrib.pop("datatype", None),
    type=element.attrib.pop("type", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_map(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Map:
  return Map(
    unicode=element.attrib.pop("unicode"),
    code=element.attrib.pop("code", None),
    ent=element.attrib.pop("ent", None),
    subst=element.attrib.pop("subst", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_ude(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Ude:
  ude = Ude(
    name=element.attrib.pop("name"),
    base=element.attrib.get("base", None),
    extra=dict(element.attrib) if keep_extra else {},
    maps=[_parse_map(child, keep_extra=keep_extra) for child in element.iter("map")],
  )
  return ude


def _parse_note(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Note:
  return Note(
    # Intentionally passing .text as is to let dataclasses handle the type error
    text=element.text,  # type: ignore
    lang=element.attrib.pop(f"{xml}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_prop(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Prop:
  return Prop(
    # Intentionally passing .text as is to let dataclasses handle the type error
    text=element.text,  # type: ignore
    type=element.attrib.pop("type"),
    lang=element.attrib.pop(f"{xml}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_header(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Header:
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


def _parse_tuv(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Tuv:
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


def _parse_tu(element: lxet._Element | pyet.Element, /, keep_extra: bool = False) -> Tu:
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


def _parse_tmx(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Tmx:
  return Tmx(
    header=_parse_header(element.find("header"), keep_extra=keep_extra),  # type: ignore
    tus=[_parse_tu(child, keep_extra=keep_extra) for child in element.iter("tu")],
    extra=dict(element.attrib) if keep_extra else {},
  )


@overload
def _map_to_element(
  map_: Map, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _map_to_element(
  map_: Map, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _map_to_element(
  map_: Map, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  return E("map", attrib=_make_attrib_dict(map_=map_, keep_extra=keep_extra))


@overload
def _ude_to_element(
  ude: Ude, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _ude_to_element(
  ude: Ude, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _ude_to_element(
  ude: Ude, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("ude", attrib=_make_attrib_dict(ude, keep_extra=keep_extra))
  elem.extend([to_element(map_, keep_extra=keep_extra, lxml=lxml) for map_ in ude.maps])  # type:ignore
  return elem


@overload
def _note_to_element(
  note: Note, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _note_to_element(
  note: Note, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _note_to_element(
  note: Note, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("note", _make_attrib_dict(note, keep_extra=keep_extra))
  elem.text = note.text
  return elem


@overload
def _prop_to_element(
  prop: Prop, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _prop_to_element(
  prop: Prop, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _prop_to_element(
  prop: Prop, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("prop", _make_attrib_dict(prop, keep_extra=keep_extra))
  elem.text = prop.text
  return elem


@overload
def _header_to_element(
  header: Header, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _header_to_element(
  header: Header, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _header_to_element(
  header: Header, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("header", _make_attrib_dict(header, keep_extra=keep_extra))
  elem.extend(
    [
      to_element(item, keep_extra=keep_extra, lxml=lxml)  # type:ignore
      for item in chain(header.notes, header.props, header.udes)
    ]
  )
  return elem


@overload
def _tuv_to_element(
  tuv: Tuv, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _tuv_to_element(
  tuv: Tuv, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _tuv_to_element(
  tuv: Tuv, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("tuv", attrib=_make_attrib_dict(tuv, keep_extra=keep_extra))
  elem.extend(
    [to_element(item, keep_extra=keep_extra) for item in chain(tuv.notes, tuv.props)]  # type:ignore
  )
  seg = E("seg")
  elem.append(seg)  # type:ignore
  _fill_inline_content(tuv.content, seg, keep_extra=keep_extra)
  return elem


@overload
def _tu_to_element(
  tu: Tu, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _tu_to_element(
  tu: Tu, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _tu_to_element(
  tu: Tu, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("tu", attrib=_make_attrib_dict(tu, keep_extra=keep_extra))
  elem.extend(
    [
      to_element(item, keep_extra=keep_extra)  # type:ignore
      for item in chain(tu.notes, tu.props, tu.tuvs)
    ]
  )
  return elem


@overload
def _tmx_to_element(
  tmx: Tmx, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _tmx_to_element(
  tmx: Tmx, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _tmx_to_element(
  tmx: Tmx, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("tmx", version="1.4")
  elem.append(_header_to_element(tmx.header, keep_extra=keep_extra, lxml=lxml))  # type: ignore
  body = E("body")
  elem.append(body)  # type: ignore
  body.extend([to_element(item, keep_extra=keep_extra, lxml=lxml) for item in tmx.tus])  # type: ignore
  return elem


@overload
def _ph_to_element(
  ph: Ph, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _ph_to_element(
  ph: Ph, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _ph_to_element(
  ph: Ph, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("ph", attrib=_make_attrib_dict(ph, keep_extra=keep_extra))
  _fill_inline_content(ph.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _bpt_to_element(
  bpt: Bpt, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _bpt_to_element(
  bpt: Bpt, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _bpt_to_element(
  bpt: Bpt, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("bpt", attrib=_make_attrib_dict(bpt, keep_extra=keep_extra))
  _fill_inline_content(bpt.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _ept_to_element(
  ept: Ept, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _ept_to_element(
  ept: Ept, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _ept_to_element(
  ept: Ept, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("ept", attrib=_make_attrib_dict(ept, keep_extra=keep_extra))
  _fill_inline_content(ept.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _it_to_element(
  it: It, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _it_to_element(
  it: It, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _it_to_element(
  it: It, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("it", attrib=_make_attrib_dict(it, keep_extra=keep_extra))
  _fill_inline_content(it.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _ut_to_element(
  ut: Ut, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _ut_to_element(
  ut: Ut, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _ut_to_element(
  ut: Ut, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("ut", attrib=_make_attrib_dict(ut, keep_extra=keep_extra))
  _fill_inline_content(ut.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _sub_to_element(
  sub: Sub, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _sub_to_element(
  sub: Sub, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _sub_to_element(
  sub: Sub, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("sub", attrib=_make_attrib_dict(sub, keep_extra=keep_extra))
  _fill_inline_content(sub.content, elem, keep_extra=keep_extra)
  return elem


@overload
def _hi_to_element(
  hi: Hi, /, keep_extra: bool, lxml: Literal[True]
) -> lxet._Element: ...
@overload
def _hi_to_element(
  hi: Hi, /, keep_extra: bool, lxml: Literal[False]
) -> pyet.Element: ...
def _hi_to_element(
  hi: Hi, /, keep_extra: bool, lxml: Literal[True] | Literal[False]
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("hi", attrib=_make_attrib_dict(hi, keep_extra=keep_extra))
  _fill_inline_content(hi.content, elem, keep_extra=keep_extra)
  return elem


@overload
def to_element(
  element: TmxElement,
  lxml: Literal[True],
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> lxet._Element: ...
@overload
def to_element(
  element: TmxElement,
  lxml: Literal[False],
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> pyet.Element: ...
def to_element(
  element: TmxElement,
  lxml: Literal[True] | Literal[False] = True,
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> lxet._Element | pyet.Element:
  """
  Converts a TmxElement to an lxml or ElementTree element.

  If `lxml` is True, the output will be an lxml element, otherwise it will be an
  ElementTree element.

  If `keep_extra` is True, the extra attributes of the element (and its children)
  will be included in the output.

  .. warning::
    Even if `validate_element` is True, the `extra` dict will NOT be validated.
    As this is NOT part of the TMX spec, it is the responsibility of the user to
    ensure that the `extra` dict is a valid mapping of strings to strings.

  Parameters
  ----------
  element : TmxElement
      The TmxElement to convert
  lxml : Literal[True] | Literal[False]
      Whether to use lxml or ElementTree, by default True
  keep_extra : bool, optional
      Whether to include extra attributes present in the element (and its children),
      by default False
  validate_element : bool, optional
      Whether to validate the element before converting it (and its children),
      by default True

  Returns
  -------
  lxet._Element | pyet.Element
      An lxml or ElementTree element representing the TmxElement

  Raises
  ------
  TypeError
      If the TmxElement is not recognized
  """
  if validate_element:
    validate(element)
  match element:
    case Map():
      return _map_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Ude():
      return _ude_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Note():
      return _note_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Prop():
      return _prop_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Header():
      return _header_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Tuv():
      return _tuv_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Tu():
      return _tu_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Tmx():
      return _tmx_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Ph():
      return _ph_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Bpt():
      return _bpt_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Ept():
      return _ept_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case It():
      return _it_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Ut():
      return _ut_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Sub():
      return _sub_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case Hi():
      return _hi_to_element(element, keep_extra=keep_extra, lxml=lxml)
    case _:
      raise TypeError(f"Unknown element {element}")


def from_element(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> TmxElement:
  """
  Converts an lxml or ElementTree element to a TmxElement object.

  Parameters
  ----------
  element : lxet._Element | pyet.Element
      The element to convert
  keep_extra : bool, optional
      Whether to keep extra attributes present in the element (and its children),
      by default False

  Returns
  -------
  TmxElement
      An instance of the appropriate TmxElement subclass

  Raises
  ------
  ValueError
      If the element is not a valid lxml or ElementTree element or the tag is not recognized
  """
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


def _check_hex_and_unicode_codepoint(string: str) -> None:
  if not isinstance(string, str):
    raise TypeError(f"Expected str, not {type(string)}")
  if not string.startswith("#x"):
    raise ValueError(f"string should start with '#x' but found {string[:2]!r}")
  try:
    code_point = int(string[2:], 16)
  except ValueError:
    raise ValueError(f"Invalid hexadecimal string {string!r}")
  try:
    chr(code_point)
  except ValueError:
    raise ValueError(f"Invalid Unicode code point {code_point!r}")


def _validate_map(map_: Map) -> None:
  _check_hex_and_unicode_codepoint(map_.unicode)
  if map_.code is not None:
    _check_hex_and_unicode_codepoint(map_.code)
  if map_.ent is not None:
    if not map_.ent.isascii():
      raise ValueError(f"ent should be ASCII but found {map_.ent!r}")
  if map_.subst is not None:
    if not map_.subst.isascii():
      raise ValueError(f"subst should be ASCII but found {map_.subst!r}")


def _validate_balanced_paired_tags(content: Iterable) -> None:
  bpt_count = Counter(bpt.i for bpt in content if isinstance(bpt, Bpt))
  ept_count = Counter(ept.i for ept in content if isinstance(ept, Ept))
  if len(bpt_count) != len(ept_count):
    raise ValueError("Number of Bpt and Ept tags must be equal")
  if bpt_count.most_common(1)[0][1] > 1:
    raise ValueError("Bpt indexes must be unique")
  if ept_count.most_common(1)[0][1] > 1:
    raise ValueError("Ept indexes must be unique")


@cache
def get_cached_type_hints(clazz: Type[Any]) -> dict[str, Type[Any]]:
  return get_type_hints(clazz)


def validate(obj: TmxElement) -> None:
  """
  Validates that the TmxElement is valid and ready for export.

  Parameters
  ----------
  obj : TmxElement
      The TmxElement to convert

  Raises
  ------
  TypeError
      If a value or the object is not of its expected type
  ValueError
      If an attribute is missing
  """
  if not isinstance(obj, TmxElement):
    raise TypeError(f"Expected a TmxElement but got {type(obj)}")
  for field in fields(obj):
    # Ignore extra as these don't follow the spec so users should be the ones
    # validating them, we're letting lxml do the validation for us instead on
    # file/string export
    if field.name == "extra":
      continue
    value, hints = getattr(obj, field.name), get_cached_type_hints(obj.__class__)  # type: ignore
    if value is None:
      if field.default is MISSING:
        raise ValueError(f"missing attribute {field.name}")
      else:
        continue
    else:
      try:
        if not isinstance(value, hints[field.name]):
          raise TypeError(f"Expected {hints[field.name]} but got {type(value)}")
      except TypeError:
        for item in value:
          if not isinstance(item, hints[field.name].__args__):
            raise TypeError(
              f"Expected one of {hints[field.name].__args__} but got {type(item)}"
            )
  if isinstance(obj, Map):
    _validate_map(obj)
  elif isinstance(obj, Tuv):
    _validate_balanced_paired_tags(obj.content)
