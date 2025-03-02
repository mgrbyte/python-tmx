from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Any, MutableSequence, Optional

__all__ = [
  "TmxElement",
  "InlineElement",
  "StructuralElement",
  "Bpt",
  "Ept",
  "It",
  "Ph",
  "Hi",
  "Ut",
  "Sub",
  "Map",
  "Ude",
  "Note",
  "Prop",
  "Header",
  "Tuv",
  "Tu",
  "Tmx",
  "POS",
  "SEGTYPE",
  "ASSOC",
]


class POS(Enum):
  BEGIN = "begin"
  END = "end"


class SEGTYPE(Enum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


class ASSOC(Enum):
  PRIOR = "p"
  FOLLOWING = "f"
  BOTH = "b"


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class TmxElement:
  extra: dict[str, str] = field(default_factory=dict, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class InlineElement(TmxElement):
  content: Any


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class StructuralElement(TmxElement):
  pass


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Bpt(InlineElement):
  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  i: int
  x: Optional[str] = field(default=None)
  type: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ept(InlineElement):
  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  i: int


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Sub(InlineElement):
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  datatype: Optional[str] = field(default=None)
  type: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class It(InlineElement):
  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  pos: POS = field(metadata={"export_func": lambda x: x.value})
  x: Optional[str] = field(default=None)
  type: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ph(InlineElement):
  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  x: Optional[str] = field(default=None)
  assoc: Optional[ASSOC] = field(
    default=None, metadata={"export_func": lambda x: x.value}
  )
  type: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Hi(InlineElement):
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  x: Optional[str] = field(default=None)
  type: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ut(InlineElement):
  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  x: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Map(StructuralElement):
  unicode: str
  code: Optional[str] = field(default=None)
  ent: Optional[str] = field(default=None)
  subst: Optional[str] = field(default=None)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ude(StructuralElement):
  name: str
  base: Optional[str] = None
  maps: MutableSequence[Map] = field(default_factory=list, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Note(StructuralElement):
  text: str = field(metadata={"exclude": True})
  lang: Optional[str] = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Prop(StructuralElement):
  text: str = field(metadata={"exclude": True})
  type: str
  lang: Optional[str] = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Header(StructuralElement):
  creationtool: str
  creationtoolversion: str
  segtype: SEGTYPE = field(metadata={"export_func": lambda x: x.value})
  tmf: str = field(metadata={"export_name": "o-tmf"})
  adminlang: str
  srclang: str
  datatype: str
  encoding: Optional[str] = field(metadata={"export_name": "o-encoding"})
  creationdate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  creationid: Optional[str] = None
  changedate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  changeid: Optional[str] = None
  notes: MutableSequence[Note] = field(default_factory=list, metadata={"exclude": True})
  props: MutableSequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  udes: MutableSequence[Ude] = field(default_factory=list, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tuv(StructuralElement):
  content: MutableSequence[str | InlineElement] = field(
    default_factory=list, metadata={"exclude": True}
  )
  lang: str = field(
    metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})
  datatype: Optional[str] = field(default=None)
  usagecount: Optional[int] = field(default=None)
  lastusagedate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  creationtool: Optional[str] = field(default=None)
  creationtoolversion: Optional[str] = field(default=None)
  creationdate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  creationid: Optional[str] = field(default=None)
  changedate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  tmf: Optional[str] = field(default=None, metadata={"export_name": "o-tmf"})
  changeid: Optional[str] = field(default=None)
  props: MutableSequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  notes: MutableSequence[Note] = field(default_factory=list, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tu(StructuralElement):
  tuid: Optional[str] = field(default=None)
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})
  datatype: Optional[str] = field(default=None)
  usagecount: Optional[int] = field(default=None)
  lastusagedate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  creationtool: Optional[str] = field(default=None)
  creationtoolversion: Optional[str] = field(default=None)
  creationdate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  creationid: Optional[str] = field(default=None)
  changedate: Optional[datetime] = field(
    default=None,
    metadata={"export_func": partial(datetime.strftime, format="%Y%m%dT%H%M%SZ")},
  )
  segtype: Optional[SEGTYPE] = field(
    default=None, metadata={"export_func": lambda x: x.value}
  )
  changeid: Optional[str] = field(default=None)
  tmf: Optional[str] = field(default=None, metadata={"export_name": "o-tmf"})
  srclang: Optional[str] = field(default=None)
  notes: MutableSequence[Note] = field(default_factory=list, metadata={"exclude": True})
  props: MutableSequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  tuvs: MutableSequence[Tuv] = field(default_factory=list, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tmx(StructuralElement):
  header: Header
  tus: MutableSequence[Tu] = field(default_factory=list, metadata={"exclude": True})
