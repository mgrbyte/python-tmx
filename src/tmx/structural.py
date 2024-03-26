"""Structural TMX tag definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from re import match
from typing import Literal

from lxml.etree import Element, ElementTree, _Element, _ElementTree

from . import XMLLANG_NAMESPACE_ATTR
from .inline import run


@dataclass(kw_only=True, slots=True)
class note:
    """Note - used for comments.

    Attributes:
        - Required:
            - text
        - Optional attributes:
            - xmllang
            - oencoding
    """

    text: str | None
    xmllang: str | None = None
    oencoding: str | None = None

    def _make_element(self) -> _Element:
        """Returns a <note> lxml Element with tmx-compliant attributes"""
        elem: _Element = Element("note", attrib=self._get_tmx_attrib())
        if self.text is None:
            raise ValueError("text cannot be None")
        else:
            elem.text = str(self.text)
        return elem

    def _get_tmx_attrib(self) -> dict[str, str]:
        """Returns a dict of the object's attribute for use in during export"""
        tmx_attrib: dict = {}
        if self.xmllang is not None:
            tmx_attrib[XMLLANG_NAMESPACE_ATTR] = str(self.xmllang)
        if self.oencoding is not None:
            tmx_attrib["o-encoding"] = str(self.oencoding)
        return tmx_attrib


@dataclass(kw_only=True, slots=True)
class prop:
    """Property - used to define the various properties of the parent element.

    Can also be used to define the properties of the document header.

    These properties are not defined by the standard.

    Attributes:
        - Required:
            - text
            - prop_type
        - Optional attributes:
            - xmllang
            - oencoding

    """

    text: str | None
    prop_type: str | None
    xmllang: str | None = None
    oencoding: str | None = None

    def _make_element(self) -> _Element:
        """Returns a <prop> lxml Element"""
        elem: _Element = Element("prop", attrib=self._get_tmx_attrib())
        if self.text is None:
            raise AttributeError("text cannot be None")
        else:
            elem.text = str(self.text)
        if self.prop_type is None:
            raise AttributeError()
        return elem

    def _get_tmx_attrib(self) -> dict[str, str]:
        """Returns a dict of the object's attribute for use in during export"""
        tmx_attrib: dict = {}
        if self.prop_type is None:
            raise ValueError("prop_type cannot be None")
        else:
            tmx_attrib["type"] = str(self.prop_type)
        if self.xmllang is not None:
            tmx_attrib[XMLLANG_NAMESPACE_ATTR] = str(self.xmllang)
        if self.oencoding is not None:
            tmx_attrib["o-encoding"] = str(self.oencoding)
        return tmx_attrib


@dataclass(kw_only=True, slots=True)
class tuv:
    """
    Translation Unit Variant - specifies text in a given language.\n
    Attributes:
        - Required:
            - xmllang
        - Optional
            - oencoding
            - datatype
            - usagecount
            - lastusagedate
            - creationtool
            - creationtoolversion
            - creationdate
            - creationid
            - changedate
            - changeid
            - otmf\n"""

    xmllang: str | None = None
    tuid: str | int | None = None
    oencoding: str | None = None
    datatype: str | None = None
    usagecount: str | int | None = None
    lastusagedate: str | datetime | None = None
    creationtool: str | None = None
    creationtoolversion: str | None = None
    creationdate: str | datetime | None = None
    creationid: str | None = None
    changedate: str | datetime | None = None
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
    changeid: str | None = None
    otmf: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)
    runs: list[run] = field(default_factory=list)

    def _make_element(self) -> _Element:
        """Returns a <tuv> lxml Element with tmx-compliant attributes.

        Includes all props and notes as lxml.etree SubElements.
        The list of runs is converted to a <seg> SubElement.
        """
        tuv_elem: _Element = Element("tuv", attrib=self._get_tmx_attrib())
        for note_obj in self.notes:
            tuv_elem.append(note_obj._make_element())
        for prop_obj in self.props:
            tuv_elem.append(prop_obj._make_element())
        seg_elem: _Element = Element("seg")
        for run_obj in self.runs:
            seg_elem.append(run_obj._element)
        fake_run: _Element = seg_elem[0]
        if fake_run.tag == "fake":
            seg_elem.text = fake_run.text
            seg_elem.remove(fake_run)
        for _run in seg_elem.iter():
            if _run.tag == "fake":
                prev_elem = _run.getprevious()
                if prev_elem and _run.text:
                    if prev_elem.tail is None:
                        prev_elem.tail = _run.text
                    else:
                        prev_elem.tail += _run.text
                seg_elem.remove(_run)
        tuv_elem.append(seg_elem)
        return tuv_elem

    def _get_tmx_attrib(self) -> dict[str, str]:
        """Returns a dict of the object's attribute for use in during export."""
        tmx_attrib: dict = {}
        if self.xmllang is None or self.xmllang == "":
            raise ValueError("xmllang cannot be None or an empty string")
        else:
            tmx_attrib[XMLLANG_NAMESPACE_ATTR] = self.xmllang
        for attribute in [
            "oencoding",
            "datatype",
            "usagecount",
            "lastusagedate",
            "creationtool",
            "creationtoolversion",
            "creationdate",
            "creationid",
            "changedate",
            "changeid",
            "otmf",
        ]:
            value = getattr(self, attribute, None)
            if value is not None:
                if attribute == "oencoding":
                    tmx_attrib["o-encoding"] = str(value)
                elif attribute in ["creationdate", "changedate", "lastusagedate"]:
                    if isinstance(value, datetime):
                        utc_offset = value.utcoffset()
                        if utc_offset is not None:
                            value = value - utc_offset
                        tmx_attrib[attribute] = value.strftime("%Y%m%dT%H%M%SZ")
                    else:
                        if not match(r"\d{8}T\d{6}", value):
                            raise ValueError(f"{attribute} format is not correct.")
                        tmx_attrib[attribute] = value
                elif attribute == "otmf":
                    tmx_attrib["o-tmf"] = str(value)
                else:
                    tmx_attrib[attribute] = value
        return tmx_attrib


@dataclass(kw_only=True, slots=True)
class tu:
    """
    Translation unit - contains the data for a given translation unit.

    Attributes:
        - Required:
            - None
        - Optional:
            - tuid
            - oencoding
            - datatype
            - usagecount
            - lastusagedate
            - creationtool
            - creationtoolversion
            - creationdate
            - creationid
            - changedate
            - segtype
            - changeid
            - otmf
            - srclang."""

    tuid: str | int | None = None
    oenconding: str | None = None
    datatype: str | None = None
    usagecount: str | int | None = None
    lastusagedate: str | datetime | None = None
    creationtool: str | None = None
    creationtoolversion: str | None = None
    creationdate: str | datetime | None = None
    creationid: str | None = None
    changedate: str | datetime | None = None
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
    changeid: str | None = None
    otmf: str | None = None
    srclang: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)
    tuvs: list[tuv] = field(default_factory=list)

    def _make_element(self) -> _Element:
        """Returns a <tu> lxml Element.

        note and prop objects are converted to children if needed.
        """
        elem: _Element = Element("tu", attrib=self._get_tmx_attrib())
        for _note in self.notes:
            elem.append(_note._make_element())
        for _prop in self.props:
            elem.append(_prop._make_element())
        for _tuv in self.tuvs:
            elem.append(_tuv._make_element())
        return elem

    def _get_tmx_attrib(self) -> dict[str, str]:
        """For use in _element function.

        Converts an object's properties to a tmx-compliant dict of attributes,
        discarding any attribute haaving a value of `None`.

        """
        tmx_attrib: dict = {}
        for attribute in [
            "tuid",
            "oencoding",
            "datatype",
            "usagecount",
            "lastusagedate",
            "creationtool",
            "creationtoolversion",
            "creationdate",
            "creationid",
            "changedate",
            "segtype",
            "changeid",
            "otmf",
            "srclang",
        ]:
            value = getattr(self, attribute, None)
            if value is not None:
                if attribute == "oencoding":
                    tmx_attrib["o-encoding"] = str(value)
                elif attribute in ["creationdate", "changedate", "lastusagedate"]:
                    if isinstance(value, datetime):
                        utc_offset = value.utcoffset()
                        if utc_offset is not None:
                            value = value - utc_offset
                        tmx_attrib[attribute] = value.strftime("%Y%m%dT%H%M%SZ")
                    else:
                        if not match(r"\d{8}T\d{6}", value):
                            raise ValueError(f"{attribute} format is not correct.")
                        tmx_attrib[attribute] = value
                elif attribute == "segtype" and str(value).lower() not in [
                    "block",
                    "paragraph",
                    "sentence",
                    "phrase",
                ]:
                    raise ValueError(
                        "segtype must be one of block, paragraph, sentence or phrase "
                        f" not {self.segtype}",
                    )
                elif attribute == "otmf":
                    tmx_attrib["o-tmf"] = str(value)
                else:
                    tmx_attrib[attribute] = value
        return tmx_attrib


@dataclass(kw_only=True, slots=True)
class header:
    """File header - contains information pertaining to the whole document.\n
    Attributes:
        - Required:
            - creationtool
            - creationtoolversion
            - segtype
            - otmf
            - adminlang
            - srclang
            - datatype.
        - Optional attributes:
            - oencoding
            - creationdate
            - creationid
            - changedate
            - changeid
            - notes
            - props\n
    """

    creationtool: str | None = None
    creationtoolversion: str | None = None
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
    otmf: str | None = None
    adminlang: str | None = None
    srclang: str | None = None
    datatype: str | None = None
    oenconding: str | None = None
    creationdate: str | datetime | None = None
    creationid: str | None = None
    changedate: str | datetime | None = None
    changeid: str | None = None
    notes: list[note] = field(default_factory=list)
    props: list[prop] = field(default_factory=list)

    def _make_element(self) -> _Element:
        """Returns a <header> lxml Element.

        note and prop objects are converted to children if needed.

        """
        elem: _Element = Element("header", attrib=self._get_tmx_attrib())
        for _note in self.notes:
            elem.append(_note._make_element())
        for _prop in self.props:
            elem.append(_prop._make_element())
        return elem

    def _get_tmx_attrib(self) -> dict[str, str]:
        """Returns a dict of the objects attribute for use in during export"""
        tmx_attrib: dict = {}
        for attribute in [
            "creationtool",
            "creationtoolversion",
            "segtype",
            "otmf",
            "adminlang",
            "srclang",
            "datatype",
            "oencoding",
            "creationdate",
            "creationid",
            "changedate",
            "changeid",
        ]:
            value = getattr(self, attribute, None)
            if value is not None:
                if attribute == "segtype" and str(value).lower() not in [
                    "block",
                    "paragraph",
                    "sentence",
                    "phrase",
                ]:
                    raise ValueError(
                        "segtype must be one of block, paragraph, sentence or phrase"
                        f"not {self.segtype}"
                    )
                elif attribute == "otmf":
                    tmx_attrib["o-tmf"] = str(value)
                elif attribute == "oencoding":
                    tmx_attrib["o-encoding"] = str(value)
                elif attribute in ["creationdate", "changedate"]:
                    if isinstance(value, datetime):
                        utc_offset = value.utcoffset()
                        if utc_offset is not None:
                            value = value - utc_offset
                        tmx_attrib[attribute] = value.strftime("%Y%m%dT%H%M%SZ")
                    else:
                        if not match(r"\d{8}T\d{6}", value):
                            raise ValueError(f"{attribute} format is not correct.")
                        tmx_attrib[attribute] = value
                else:
                    tmx_attrib[attribute] = value
        for required in [
            "creationtool",
            "creationtoolversion",
            "segtype",
            "o-tmf",
            "adminlang",
            "srclang",
            "datatype",
        ]:
            if required not in tmx_attrib.keys():
                raise AttributeError(f"Missing required attribute: {required}")
        return tmx_attrib


@dataclass(kw_only=True, slots=True)
class tmx:
    Header: header | None = None
    tus: list[tu] | None = field(default_factory=list)

    def export(self, dest: str | Path):
        tmx_root: _Element = Element("tmx", attrib={"version": "1.4"})
        if self.Header:
            tmx_root.append(self.Header._make_element())
        body_elem: _Element = Element("body")
        tmx_root.append(body_elem)
        if self.tus:
            for tu_obj in self.tus:
                body_elem.append(tu_obj._make_element())
        tmx_tree: _ElementTree = ElementTree(tmx_root)
        with Path(dest).open("wb") as f:
            tmx_tree.write(f, encoding="utf-8", xml_declaration=True)