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
  """
  Whether an isolated tag :class:`It` is a beginning or and ending tag.
  """

  BEGIN = "begin"
  """
  Beginning tag
  """
  END = "end"
  """
  Ending tag
  """


class SEGTYPE(Enum):
  """
  Specifies the kind of segmentation. If a :class:`Tu` doesn't specify its segtype,
  CAT tools will default to the one in the :class:`Header` tag.
  """

  BLOCK = "block"
  """
  Used when segmentation does not correspond to one of the other values.
  """
  PARAGRAPH = "paragraph"
  """
  Used when a :class:`Tu` contains multiple multiple sentences.
  """
  SENTENCE = "sentence"
  """
  Used when a :class:`Tu` contains a single sentence.
  """
  PHRASE = "phrase"
  """
  Used when a :class:`Tu` contains single words or short phrases, not necessarily
  full sentences.
  """


class ASSOC(Enum):
  """
  Specifies whether a :class:`Ph` is associated with the previous part of the text,
  the next part of the text, or both.
  """

  PRIOR = "p"
  """
  Associated with the previous part of the text.
  """
  FOLLOWING = "f"
  """
  Associated with the next part of the text.
  """
  BOTH = "b"
  """
  Associated with both the previous and next parts of the text.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class TmxElement:
  """
  Base class for all elements in a TMX file.
  """

  extra: dict[str, str] = field(default_factory=dict, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class InlineElement(TmxElement):
  """
  Base class for all inline elements in a TMX file.
  """

  content: Any


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class StructuralElement(TmxElement):
  """
  Base class for all structural elements in a TMX file.
  """

  pass


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Bpt(InlineElement):
  """
  *Begin Paired Tag* - Delimits the beginning of a paired sequence of native code. Each :class:`Bpt`
  inside of a :class:`Tuv` must have a corresponding :class:`Ept`.
  """

  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Bpt`.
  """
  i: int
  """
  *Internal matching* - Used to pair :class:`Bpt` elements with their corresponding
  :class:`Ept` elements. Must be unique within a :class:`Tuv`. Required.
  """
  x: Optional[str] = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`Ept` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: Optional[str] = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ept(InlineElement):
  """
  *End Paired Tag* - Delimits the end of a paired sequence of native code. Each :class:`Ept` inside of
  a :class:`Tuv` must have a corresponding :class:`Bpt`.
  """

  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Ept`.
  """
  i: int
  """
  *Internal matching* - Used to pair :class:`Ept` elements with their corresponding
  :class:`Bpt` elements. Must be unique within a :class:`Tuv`. Required.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Sub(InlineElement):
  """
  *Sub Flow* - Delimits sub-flow text inside a sequence of native code, e.g. the alt-text of
  a <img /> tag.
  """

  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Sub`.
  """
  datatype: Optional[str] = field(default=None)
  """
  *Datatype* - Used to specify the type of data contained. Optional, by default None.
  """
  type: Optional[str] = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class It(InlineElement):
  """
  *Isolated Tag* - Delimits a beginning/ending sequence of native codes that does not have its
  corresponding ending/beginning within the segment.
  """

  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`It`.
  """
  pos: POS = field(metadata={"export_func": lambda x: x.value})
  """
  *Position* - Indicates whether an isolated tag :class:`It` is a beginning or
  and ending tag. Required.
  """
  x: Optional[str] = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`It` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: Optional[str] = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ph(InlineElement):
  """
  *Placeholder* - Delimits a sequence of native standalone codes in the segment.
  """

  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Ph`.
  """
  x: Optional[str] = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that a :class:`Ph` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  assoc: Optional[ASSOC] = field(
    default=None, metadata={"export_func": lambda x: x.value}
  )
  """
  *Association* - Specifies whether a :class:`Ph` is associated with the previous
  part of the text, the next part of the text, or both. Optional, by default None.
  """
  type: Optional[str] = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Hi(InlineElement):
  """
  *Highlight* - Delimits a section of text that has special meaning.
  """

  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Hi`.
  """
  x: Optional[str] = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that a :class:`Hi` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: Optional[str] = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.  
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ut(InlineElement):
  """
  *Unknown Tag* - Delimit a sequence of native unknown codes in the segment.

  .. warning::
    This element is deprecated. It is still supported for compatibility with older
    versions of TMX, but it is not recommended for new TMX files.
  """

  content: MutableSequence[str | Sub] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Ut`.
  """
  x: Optional[str] = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`Ut` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Map(StructuralElement):
  """
  *Mapping* - Used to map character and some of their properties.
  """

  unicode: str
  """
  *Unicode* - The Unicode character the mapping is for. A valid Unicode value
  (including values in the Private Use areas) in hexadecimal format.
  For example: unicode="#xF8FF". Required.
  """
  code: Optional[str] = field(default=None)
  """
  *Code* - The code-point value corresponding to the unicode character.
  A hexadecimal value prefixed with "#x". For example: code="#x9F".
  Optional, by default None.
  """
  ent: Optional[str] = field(default=None)
  """
  *Entity* - The entity name corresponding to the unicode character.
  Text in ASCII. For example: ent="copy". Optional, by default None.
  """
  subst: Optional[str] = field(default=None)
  """
  *Substitution* - What to substitute the unicode character with. Text in ASCII.
  For example: subst="copy". Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ude(StructuralElement):
  """
  *User-Defined encoding* - Used to define a user-defined encoding.
  """

  name: str
  """
  *Name* - The name of the encoding. Required.
  """
  base: Optional[str] = None
  """
  *Base* - The encoding upon which the re-mapping is based. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.

  .. note::
    If at least one :class:`Map` element has a :attr:`code` attribute, the
    :attr:`base` attribute is required.
  """
  maps: MutableSequence[Map] = field(default_factory=list, metadata={"exclude": True})
  """
  A MutableSequence of :class:`Map` elements. By default an empty list.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Note(StructuralElement):
  """
  *Note* - Used to provide information about the parent element.
  """

  text: str = field(metadata={"exclude": True})
  """
  The text of the :class:`Note`.
  """
  lang: Optional[str] = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  """
  *Language* - The language of the :class:`Note`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Optional, by default None. Optional,
  by default None.
  """
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Note`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Prop(StructuralElement):
  """
  *Property* - Used to provide information about specific properties of the parent
  element.

  These properties are not defined by the standard. The "text" can be any
  anything as long as it is in string format. By convention, values for the
  "type" attribute that are not defined by the standard should be prefixed with
  "x-". For example, "x-my-custom-type".
  """

  text: str = field(metadata={"exclude": True})
  """
  The text of the :class:`Prop`.
  """
  type: str
  """
  *Type* - The type of the :class:`Prop`. Required.

  .. note::
    The "type" attribute is not defined by the standard. The "text" can be any
    anything as long as it is in string format. By convention, values for the
    "type" attribute that are not defined by the standard should be prefixed with
    "x-". For example, "x-my-custom-type".
  """
  lang: Optional[str] = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  """
  *Language* - The language of the :class:`Prop`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Optional, by default None.
  """
  encoding: Optional[str] = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Prop`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """


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
