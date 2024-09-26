from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, MutableSequence, Optional, final

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializationInfo,
    field_serializer,
)

from .errors import MissingAttributeError

__XML__ = "{http://www.w3.org/XML/1998/namespace}"


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


class TmxElement(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)

    @field_serializer("x", "i", "usagecount", check_fields=False)
    @classmethod
    def serialize_int(cls, num: int) -> str:
        return str(num)

    @field_serializer("creationdate", "changedate", "lastusagedate", check_fields=False)
    @classmethod
    def serialize_dt(cls, date: datetime) -> str:
        return date.strftime(r"%Y%m%dT%H%M%SZ")


class InlineElement(TmxElement):
    content: Any


class Note(TmxElement):
    text: str = Field(exclude=True)
    lang: Optional[str] = Field(default=None, serialization_alias=f"{__XML__}lang")
    encoding: Optional[str] = Field(default=None, serialization_alias="o-encoding")


class Prop(TmxElement):
    text: str = Field(exclude=True)
    type: str
    lang: Optional[str] = Field(default=None, serialization_alias=f"{__XML__}lang")
    encoding: Optional[str] = Field(default=None, serialization_alias="o-encoding")


class Map(TmxElement):
    unicode: str
    code: Optional[str] = None
    ent: Optional[str] = None
    subst: Optional[str] = None


class Ude(TmxElement):
    maps: Optional[MutableSequence[Map]] = Field(default_factory=list, exclude=True)
    name: str
    base: Optional[str] = None

    @field_serializer("base")
    @classmethod
    def check_base_needed(
        cls, base: Optional[str], info: SerializationInfo
    ) -> Optional[str]:
        maps: Optional[MutableSequence[Map]] = info.context
        if maps and len(maps) and not base:
            for map in maps:
                if map.code:
                    raise MissingAttributeError("base", "ude")
        return base


class Header(TmxElement):
    creationtool: str
    creationtoolversion: str
    segtype: SEGTYPE
    tmf: str = Field(serialization_alias="o-tmf")
    adminlang: str
    srclang: str
    datatype: str
    encoding: Optional[str] = Field(serialization_alias="o-encoding")
    creationdate: Optional[datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[datetime] = None
    changeid: Optional[str] = None
    props: MutableSequence[Prop] = Field(default_factory=list, exclude=True)
    notes: MutableSequence[Note] = Field(default_factory=list, exclude=True)
    udes: MutableSequence[Ude] = Field(default_factory=list, exclude=True)


class Tuv(TmxElement):
    lang: str = Field(serialization_alias=f"{__XML__}lang")
    encoding: Optional[str] = Field(default=None, serialization_alias="o-encoding")
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[datetime] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = Field(default=None, serialization_alias="o-tmf")
    props: MutableSequence[Prop] = Field(default_factory=list, exclude=True)
    notes: MutableSequence[Note] = Field(default_factory=list, exclude=True)
    segment: MutableSequence[str | InlineElement] = Field(
        default_factory=list, exclude=True
    )


class Tu(TmxElement):
    tuid: Optional[str] = None
    encoding: Optional[str] = Field(default=None, serialization_alias="o-encoding")
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
    tmf: Optional[str] = Field(default=None, serialization_alias="o-tmf")
    srclang: Optional[str] = None
    props: MutableSequence[Prop] = Field(default_factory=list, exclude=True)
    notes: MutableSequence[Note] = Field(default_factory=list, exclude=True)
    tuvs: MutableSequence[Tuv] = Field(default_factory=list, exclude=True)


class Tmx(TmxElement):
    header: Header = Field(exclude=True)
    tus: MutableSequence[Tu] = Field(exclude=True)


class Sub(TmxElement):
    content: MutableSequence[str | InlineElement | Ut] = Field(
        default_factory=list, exclude=True
    )
    datatype: Optional[str] = None
    type: Optional[str] = None


class Ut(TmxElement):
    content: MutableSequence[str | Sub] = Field(default_factory=list, exclude=True)
    x: Optional[int] = None


class Ph(InlineElement):
    content: MutableSequence[str | Sub] = Field(default_factory=list, exclude=True)
    x: Optional[int] = None
    type: Optional[str] = None
    assoc: Optional[ASSOC] = None


class Bpt(InlineElement):
    content: MutableSequence[str | Sub] = Field(default_factory=list, exclude=True)
    i: int
    x: Optional[int] = None
    type: Optional[str] = None


class Ept(InlineElement):
    content: MutableSequence[str | Sub] = Field(default_factory=list, exclude=True)
    i: int


class Hi(InlineElement):
    content: MutableSequence[str | InlineElement | Ut] = Field(
        default_factory=list, exclude=True
    )
    x: Optional[int] = None
    type: Optional[str] = None


class It(InlineElement):
    content: MutableSequence[str | Sub] = Field(default_factory=list, exclude=True)
    pos: POS
    x: Optional[int] = None
    type: Optional[str] = None
