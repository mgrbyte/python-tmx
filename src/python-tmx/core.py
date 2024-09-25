from dataclasses import dataclass
from typing import Optional


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
