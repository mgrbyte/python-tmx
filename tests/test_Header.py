import datetime as dt
import xml.etree.ElementTree as pyet

import lxml.etree as lxet
import pytest

from PythonTmx.classes import ENGINE, SEGTYPE, Header, Map


@pytest.fixture
def correct_elem_python() -> pyet.Element:
  return pyet.fromstring(
    r"""<header creationtool="XYZTool" creationtoolversion="1.01-023" datatype="PlainText" segtype="sentence" adminlang="en-us" srclang="EN" o-tmf="ABCTransMem" creationdate="20020101T163812Z" creationid="ThomasJ" changedate="20020413T023401Z" changeid="Amity" o-encoding="iso-8859-1"><note>This is a note at document level.</note><prop type="RTFPreamble">{\rtf1\ansi\tag etc...{\fonttbl}</prop><ude name="MacRoman" base="Macintosh"><map unicode="#xF8FF" code="#xF0" ent="Apple_logo" subst="[Apple]"/></ude></header>"""
  )


@pytest.fixture
def correct_elem_lxml() -> lxet._Element:
  return lxet.fromstring(
    r"""<header creationtool="XYZTool" creationtoolversion="1.01-023" datatype="PlainText" segtype="sentence" adminlang="en-us" srclang="EN" o-tmf="ABCTransMem" creationdate="20020101T163812Z" creationid="ThomasJ" changedate="20020413T023401Z" changeid="Amity" o-encoding="iso-8859-1"><note>This is a note at document level.</note><prop type="RTFPreamble">{\rtf1\ansi\tag etc...{\fonttbl}</prop><ude name="MacRoman" base="Macintosh"><map unicode="#xF8FF" code="#xF0" ent="Apple_logo" subst="[Apple]"/></ude></header>"""
  )


class TestHeader:
  def test_init(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      datatype="PlainText",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      creationdate=dt.datetime(2002, 1, 1, 16, 38, 12),
      creationid="ThomasJ",
      changedate=dt.datetime(2002, 4, 13, 2, 34, 1),
      changeid="Amity",
      encoding="iso-8859-1",
    )
    assert header.creationtool == "XYZTool"
    assert header.creationtoolversion == "1.01-023"
    assert header.datatype == "PlainText"
    assert header.segtype is SEGTYPE.SENTENCE
    assert header.adminlang == "en-us"
    assert header.srclang == "EN"
    assert header.tmf == "ABCTransMem"
    assert header.creationdate == dt.datetime(2002, 1, 1, 16, 38, 12)
    assert header.creationid == "ThomasJ"
    assert header.changedate == dt.datetime(2002, 4, 13, 2, 34, 1)
    assert header.changeid == "Amity"
    assert header.encoding == "iso-8859-1"
    assert header.notes == []
    assert header.props == []
    assert header.udes == []

  def test_empy_init(self) -> None:
    with pytest.raises(TypeError):
      Header()

  def test_minimum_init(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      datatype="PlainText",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
    )
    assert header.creationtool == "XYZTool"
    assert header.creationtoolversion == "1.01-023"
    assert header.datatype == "PlainText"
    assert header.segtype is SEGTYPE.SENTENCE
    assert header.adminlang == "en-us"
    assert header.srclang == "EN"
    assert header.tmf == "ABCTransMem"
    assert header.creationdate is None
    assert header.creationid is None
    assert header.changedate is None
    assert header.changeid is None
    assert header.encoding is None
    assert header.notes == []
    assert header.props == []
    assert header.udes == []

  def test_from_element_python(self, correct_elem_python: pyet.Element) -> None:
    header = Header.from_element(correct_elem_python)
    assert (
      header.creationtool == "XYZTool" == correct_elem_python.attrib["creationtool"]
    )
    assert (
      header.creationtoolversion
      == "1.01-023"
      == correct_elem_python.attrib["creationtoolversion"]
    )
    assert header.datatype == "PlainText" == correct_elem_python.attrib["datatype"]
    assert header.segtype.value == "sentence" == correct_elem_python.attrib["segtype"]
    assert header.adminlang == "en-us" == correct_elem_python.attrib["adminlang"]
    assert header.srclang == "EN" == correct_elem_python.attrib["srclang"]
    assert header.tmf == "ABCTransMem" == correct_elem_python.attrib["o-tmf"]
    assert header.creationdate == dt.datetime.fromisoformat(
      correct_elem_python.attrib["creationdate"]
    )
    assert header.creationid == "ThomasJ" == correct_elem_python.attrib["creationid"]
    assert header.changedate == dt.datetime.fromisoformat(
      correct_elem_python.attrib["changedate"]
    )
    assert len(header.notes) == 1 == len(correct_elem_python.findall("note"))
    assert len(header.props) == 1 == len(correct_elem_python.findall("prop"))
    assert len(header.udes) == 1 == len(correct_elem_python.findall("ude"))
    assert header.notes[0].text == "This is a note at document level."
    assert header.notes[0].lang is None
    assert header.notes[0].encoding is None
    assert header.props[0].text == r"{\rtf1\ansi\tag etc...{\fonttbl}"
    assert header.props[0].type == "RTFPreamble"
    assert header.props[0].lang is None
    assert header.props[0].encoding is None
    assert header.udes[0].name == "MacRoman"
    assert header.udes[0].base == "Macintosh"
    assert header.udes[0].maps == [
      Map(
        unicode="#xF8FF",
        code="#xF0",
        ent="Apple_logo",
        subst="[Apple]",
      )
    ]

  def test_from_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    now = dt.datetime.now()
    header = Header.from_element(correct_elem_python, creationdate=now, changedate=None)
    assert header.creationdate == now
    assert header.changedate is None
    assert (
      header.creationtool == "XYZTool" == correct_elem_python.attrib["creationtool"]
    )
    assert (
      header.creationtoolversion
      == "1.01-023"
      == correct_elem_python.attrib["creationtoolversion"]
    )
    assert header.datatype == "PlainText" == correct_elem_python.attrib["datatype"]
    assert header.segtype.value == "sentence" == correct_elem_python.attrib["segtype"]
    assert header.adminlang == "en-us" == correct_elem_python.attrib["adminlang"]
    assert header.srclang == "EN" == correct_elem_python.attrib["srclang"]
    assert header.tmf == "ABCTransMem" == correct_elem_python.attrib["o-tmf"]
    assert header.creationid == "ThomasJ" == correct_elem_python.attrib["creationid"]
    assert header.changeid == "Amity" == correct_elem_python.attrib["changeid"]
    assert len(header.notes) == 1 == len(correct_elem_python.findall("note"))
    assert len(header.props) == 1 == len(correct_elem_python.findall("prop"))
    assert len(header.udes) == 1 == len(correct_elem_python.findall("ude"))
    assert header.notes[0].text == "This is a note at document level."
    assert header.notes[0].lang is None
    assert header.notes[0].encoding is None
    assert header.props[0].text == r"{\rtf1\ansi\tag etc...{\fonttbl}"
    assert header.props[0].type == "RTFPreamble"
    assert header.props[0].lang is None
    assert header.props[0].encoding is None
    assert header.udes[0].name == "MacRoman"
    assert header.udes[0].base == "Macintosh"
    assert header.udes[0].maps == [
      Map(
        unicode="#xF8FF",
        code="#xF0",
        ent="Apple_logo",
        subst="[Apple]",
      )
    ]

  def test_from_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    header = Header.from_element(correct_elem_lxml)
    assert header.creationtool == "XYZTool" == correct_elem_lxml.attrib["creationtool"]
    assert (
      header.creationtoolversion
      == "1.01-023"
      == correct_elem_lxml.attrib["creationtoolversion"]
    )
    assert header.datatype == "PlainText" == correct_elem_lxml.attrib["datatype"]
    assert header.segtype.value == "sentence" == correct_elem_lxml.attrib["segtype"]
    assert header.adminlang == "en-us" == correct_elem_lxml.attrib["adminlang"]
    assert header.srclang == "EN" == correct_elem_lxml.attrib["srclang"]
    assert header.tmf == "ABCTransMem" == correct_elem_lxml.attrib["o-tmf"]
    assert header.creationdate == dt.datetime.fromisoformat(
      correct_elem_lxml.attrib["creationdate"]
    )
    assert header.creationid == "ThomasJ" == correct_elem_lxml.attrib["creationid"]
    assert header.changedate == dt.datetime.fromisoformat(
      correct_elem_lxml.attrib["changedate"]
    )
    assert header.changeid == "Amity" == correct_elem_lxml.attrib["changeid"]
    assert len(header.notes) == 1 == len(correct_elem_lxml.findall("note"))
    assert len(header.props) == 1 == len(correct_elem_lxml.findall("prop"))
    assert len(header.udes) == 1 == len(correct_elem_lxml.findall("ude"))
    assert header.notes[0].text == "This is a note at document level."
    assert header.notes[0].lang is None
    assert header.notes[0].encoding is None
    assert header.props[0].text == r"{\rtf1\ansi\tag etc...{\fonttbl}"
    assert header.props[0].type == "RTFPreamble"
    assert header.props[0].lang is None
    assert header.props[0].encoding is None
    assert header.udes[0].name == "MacRoman"
    assert header.udes[0].base == "Macintosh"
    assert header.udes[0].maps == [
      Map(
        unicode="#xF8FF",
        code="#xF0",
        ent="Apple_logo",
        subst="[Apple]",
      )
    ]

  def test_from_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    now = dt.datetime.now()
    header = Header.from_element(correct_elem_lxml, creationdate=now, changedate=None)
    assert header.creationdate == now
    assert header.changedate is None
    assert header.creationtool == "XYZTool" == correct_elem_lxml.attrib["creationtool"]
    assert (
      header.creationtoolversion
      == "1.01-023"
      == correct_elem_lxml.attrib["creationtoolversion"]
    )
    assert header.datatype == "PlainText" == correct_elem_lxml.attrib["datatype"]
    assert header.segtype.value == "sentence" == correct_elem_lxml.attrib["segtype"]
    assert header.adminlang == "en-us" == correct_elem_lxml.attrib["adminlang"]
    assert header.srclang == "EN" == correct_elem_lxml.attrib["srclang"]
    assert header.tmf == "ABCTransMem" == correct_elem_lxml.attrib["o-tmf"]
    assert header.creationid == "ThomasJ" == correct_elem_lxml.attrib["creationid"]
    assert header.changeid == "Amity" == correct_elem_lxml.attrib["changeid"]
    assert len(header.notes) == 1 == len(correct_elem_lxml.findall("note"))
    assert len(header.props) == 1 == len(correct_elem_lxml.findall("prop"))
    assert len(header.udes) == 1 == len(correct_elem_lxml.findall("ude"))
    assert header.notes[0].text == "This is a note at document level."
    assert header.notes[0].lang is None
    assert header.notes[0].encoding is None
    assert header.props[0].text == r"{\rtf1\ansi\tag etc...{\fonttbl}"
    assert header.props[0].type == "RTFPreamble"
    assert header.props[0].lang is None
    assert header.props[0].encoding is None
    assert header.udes[0].name == "MacRoman"
    assert header.udes[0].base == "Macintosh"
    assert header.udes[0].maps == [
      Map(
        unicode="#xF8FF",
        code="#xF0",
        ent="Apple_logo",
        subst="[Apple]",
      )
    ]

  def test_to_element_python(self, correct_elem_python: pyet.Element) -> None:
    header = Header.from_element(correct_elem_python)
    header_elem = header.to_element(ENGINE.PYTHON)
    assert header_elem.tag == correct_elem_python.tag == "header"
    assert header_elem.attrib == correct_elem_python.attrib
    assert len(header_elem.findall("note")) == 1
    assert len(header_elem.findall("prop")) == 1
    assert len(header_elem.findall("ude")) == 1

  def test_to_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    header = Header.from_element(correct_elem_python)
    header_elem = header.to_element(ENGINE.PYTHON, creationtool="new tool")
    assert header_elem.tag == "header" == correct_elem_python.tag
    assert header_elem.attrib["creationtool"] == "new tool"
    assert (
      header_elem.attrib["creationtoolversion"]
      == correct_elem_python.attrib["creationtoolversion"]
    )
    assert header_elem.attrib["datatype"] == correct_elem_python.attrib["datatype"]
    assert header_elem.attrib["segtype"] == correct_elem_python.attrib["segtype"]
    assert header_elem.attrib["adminlang"] == correct_elem_python.attrib["adminlang"]
    assert header_elem.attrib["srclang"] == correct_elem_python.attrib["srclang"]
    assert header_elem.attrib["o-tmf"] == correct_elem_python.attrib["o-tmf"]
    assert (
      header_elem.attrib["creationdate"] == correct_elem_python.attrib["creationdate"]
    )
    assert header_elem.attrib["creationid"] == correct_elem_python.attrib["creationid"]
    assert header_elem.attrib["changedate"] == correct_elem_python.attrib["changedate"]
    assert header_elem.attrib["changeid"] == correct_elem_python.attrib["changeid"]
    assert len(header_elem.findall("note")) == 1
    assert len(header_elem.findall("prop")) == 1
    assert len(header_elem.findall("ude")) == 1

  def test_to_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    header = Header.from_element(correct_elem_lxml)
    header_elem = header.to_element(ENGINE.LXML)
    assert header_elem.tag == correct_elem_lxml.tag == "header"
    assert header_elem.attrib == dict(correct_elem_lxml.attrib)
    assert len(header_elem.findall("note")) == 1
    assert len(header_elem.findall("prop")) == 1
    assert len(header_elem.findall("ude")) == 1

  def test_to_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    header = Header.from_element(correct_elem_lxml)
    header_elem = header.to_element(ENGINE.LXML, creationtool="new tool")
    assert header_elem.tag == "header" == correct_elem_lxml.tag
    assert header_elem.attrib["creationtool"] == "new tool"
    assert (
      header_elem.attrib["creationtoolversion"]
      == correct_elem_lxml.attrib["creationtoolversion"]
    )
    assert header_elem.attrib["datatype"] == correct_elem_lxml.attrib["datatype"]
    assert header_elem.attrib["segtype"] == correct_elem_lxml.attrib["segtype"]
    assert header_elem.attrib["adminlang"] == correct_elem_lxml.attrib["adminlang"]
    assert header_elem.attrib["srclang"] == correct_elem_lxml.attrib["srclang"]
    assert header_elem.attrib["o-tmf"] == correct_elem_lxml.attrib["o-tmf"]
    assert (
      header_elem.attrib["creationdate"] == correct_elem_lxml.attrib["creationdate"]
    )
    assert header_elem.attrib["creationid"] == correct_elem_lxml.attrib["creationid"]
    assert header_elem.attrib["changedate"] == correct_elem_lxml.attrib["changedate"]
    assert header_elem.attrib["changeid"] == correct_elem_lxml.attrib["changeid"]
    assert len(header_elem.findall("note")) == 1
    assert len(header_elem.findall("prop")) == 1
    assert len(header_elem.findall("ude")) == 1

  def test_from_element_invalid(self) -> None:
    with pytest.raises(ValueError):
      Header.from_element(pyet.Element("test"))

  def test_incorrect_attrib_type_export(self) -> None:
    header = Header(
      creationtool=123,
      creationtoolversion="1.01-023",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    with pytest.raises(TypeError):
      header.to_element()

  def test_incorrect_segtype_export(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      segtype="sentence",
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    with pytest.raises(TypeError):
      header.to_element()

  def test_unknown_non_iso_dt(self) -> None:
    with pytest.warns(UserWarning):
      Header.from_element(
        pyet.Element(
          "header",
          attrib={
            "creationtool": "XYZTool",
            "creationtoolversion": "1.01-023",
            "datatype": "PlainText",
            "segtype": "sentence",
            "adminlang": "en-us",
            "srclang": "EN",
            "o-tmf": "ABCTransMem",
            "creationdate": "hello",
          },
        )
      )
    with pytest.warns(UserWarning):
      Header.from_element(
        pyet.Element(
          "header",
          attrib={
            "creationtool": "XYZTool",
            "creationtoolversion": "1.01-023",
            "datatype": "PlainText",
            "segtype": "sentence",
            "adminlang": "en-us",
            "srclang": "EN",
            "o-tmf": "ABCTransMem",
            "changedate": "hello",
          },
        )
      )

  def test_unknown_non_iso_dt_kwargs(self) -> None:
    with pytest.warns(UserWarning):
      Header.from_element(
        pyet.Element(
          "header",
          attrib={
            "creationtool": "XYZTool",
            "creationtoolversion": "1.01-023",
            "datatype": "PlainText",
            "segtype": "sentence",
            "adminlang": "en-us",
            "srclang": "EN",
            "o-tmf": "ABCTransMem",
          },
        ),
        creationdate="hello",
      )
    with pytest.warns(UserWarning):
      Header.from_element(
        pyet.Element(
          "header",
          attrib={
            "creationtool": "XYZTool",
            "creationtoolversion": "1.01-023",
            "datatype": "PlainText",
            "segtype": "sentence",
            "adminlang": "en-us",
            "srclang": "EN",
            "o-tmf": "ABCTransMem",
          },
        ),
        changedate="hello",
      )

  def test_incorrect_segtype(self) -> None:
    with pytest.warns(UserWarning):
      Header.from_element(
        pyet.Element(
          "header",
          attrib={
            "creationtool": "XYZTool",
            "creationtoolversion": "1.01-023",
            "datatype": "PlainText",
            "segtype": "hello",
            "adminlang": "en-us",
            "srclang": "EN",
            "o-tmf": "ABCTransMem",
            "creationdate": "20020101T163812Z",
          },
        )
      )

  def test_incorrect_attrib_type(self) -> None:
    header = Header(
      creationtool=123,
      creationtoolversion="1.01-023",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    with pytest.raises(TypeError):
      header.to_element()

  def test_incorrect_note(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    header.notes.append(123)
    with pytest.raises(TypeError):
      header.to_element()

  def test_incorrect_prop(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    header.props.append(123)
    with pytest.raises(TypeError):
      header.to_element()

  def test_incorrect_ude(self) -> None:
    header = Header(
      creationtool="XYZTool",
      creationtoolversion="1.01-023",
      segtype=SEGTYPE.SENTENCE,
      adminlang="en-us",
      srclang="EN",
      tmf="ABCTransMem",
      datatype="Plaintext",
    )
    header.udes.append(123)
    with pytest.raises(TypeError):
      header.to_element()
