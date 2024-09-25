from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import MutableSequence, Optional, final


@final
class SEGTYPE(Enum):
    BLOCK = "block"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    PHRASE = "phrase"


@final
class POS(Enum):
    BEGIN = "begin"
    END = "end"


@final
class ASSOC(Enum):
    P = "p"
    F = "f"
    B = "b"


class Inline:
    pass


@dataclass(slots=True, kw_only=True)
class Note:
    text: str
    lang: Optional[str] = None
    encoding: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Prop:
    text: str
    type: str
    lang: Optional[str] = None
    encoding: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Map:
    unicode: str
    code: Optional[str] = None
    ent: Optional[str] = None
    subst: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Ude:
    name: str
    base: Optional[str] = None
    maps: Optional[MutableSequence[Map]] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Header:
    creationtool: str
    creationtoolversion: str
    segtype: SEGTYPE
    tmf: str
    adminlang: str
    srclang: str
    datatype: str
    encoding: Optional[str] = None
    creationdate: Optional[datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[datetime] = None
    changeid: Optional[str] = None
    props: MutableSequence[Prop] = field(default_factory=list)
    notes: MutableSequence[Note] = field(default_factory=list)
    udes: MutableSequence[Ude] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Tuv:
    lang: str
    encoding: Optional[str] = None
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[datetime] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = None
    props: MutableSequence[Prop] = field(default_factory=list)
    notes: MutableSequence[Note] = field(default_factory=list)
    segment: MutableSequence[str | Inline] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Tu:
    tuid: Optional[str] = None
    encoding: Optional[str] = None
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[datetime] = None
    segtype: Optional[SEGTYPE] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = None
    srclang: Optional[str] = None
    props: MutableSequence[Prop] = field(default_factory=list)
    notes: MutableSequence[Note] = field(default_factory=list)
    tuvs: MutableSequence[Tuv] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Tmx:
    header: Header
    tus: MutableSequence[Tu] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Sub:
    content: MutableSequence[str | Inline] = field(default_factory=list)
    datatype: Optional[str] = None
    type: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Ph(Inline):
    content: MutableSequence[str | Sub] = field(default_factory=list)
    x: Optional[int] = None
    type: Optional[str] = None
    assoc: Optional[ASSOC] = None


@dataclass(slots=True, kw_only=True)
class Bpt(Inline):
    content: MutableSequence[str | Sub] = field(default_factory=list)
    i: int
    x: Optional[int] = None
    type: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Ept(Inline):
    content: MutableSequence[str | Sub] = field(default_factory=list)
    i: int


@dataclass(slots=True, kw_only=True)
class Hi(Inline):
    content: MutableSequence[str | Inline] = field(default_factory=list)
    x: Optional[int] = None
    type: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class It(Inline):
    content: MutableSequence[str | Sub] = field(default_factory=list)
    pos: POS
    x: Optional[int] = None
    type: Optional[str] = None


@dataclass(slots=True, kw_only=True)
class Ut(Inline):
    content: MutableSequence[str | Sub] = field(default_factory=list)
    x: Optional[int] = None
