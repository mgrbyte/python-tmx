"""
Tests for the Header class
"""

from datetime import datetime
from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Header, Map, Note, Prop, Ude


class TestHeader(TestCase):
    def test_create_export_empty_header(self):
        header = Header()
        for attr in header.__slots__:
            if attr in ("notes", "props", "udes"):
                self.assertEqual(getattr(header, attr), [])
            else:
                self.assertIsNone(getattr(header, attr))
        with self.assertRaises(AttributeError):
            header.to_element()

    def test_create_header_from_element(self):
        elem = fromstring("""<header creationtool="XYZTool"
  creationtoolversion="1.01-023"
  datatype="PlainText"
  segtype="sentence"
  adminlang="en-us"
  srclang="EN"
  o-tmf="ABCTransMem"
  creationdate="20020101T163812Z"
  creationid="ThomasJ"
  changedate="20020413T023401Z"
  changeid="Amity"
  o-encoding="iso-8859-1">
  <note>This is a note at document level.</note>
  <prop type="RTFPreamble">prop text</prop>
  <ude creationtool="MacRoman"
    base="Macintosh">
    <map unicode="#xF8FF"
      code="#xF0"
      ent="Apple_logo"
      subst="[Apple]" />
  </ude>
</header>""")
        header = Header(elem)
        for attr in (
            "creationtool",
            "creationtoolversion",
            "segtype",
            "adminlang",
            "srclang",
            "datatype",
            "creationid",
            "changeid",
        ):
            self.assertEqual(getattr(header, attr), elem.get(attr))
        self.assertEqual(getattr(header, "tmf"), elem.get("o-tmf"))
        self.assertEqual(getattr(header, "encoding"), elem.get("o-encoding"))
        self.assertEqual(
            getattr(header, "creationdate"), datetime(2002, 1, 1, 16, 38, 12)
        )
        self.assertEqual(getattr(header, "changedate"), datetime(2002, 4, 13, 2, 34, 1))
        self.assertIsInstance(header.notes, list)
        self.assertIsInstance(header.props, list)
        self.assertIsInstance(header.udes, list)
        self.assertEqual(len(header.notes), 1)
        self.assertEqual(len(header.props), 1)
        self.assertEqual(len(header.udes), 1)
        self.assertIsInstance(header.notes[0], Note)
        self.assertEqual(header.notes[0].text, elem.find("note").text)
        self.assertIsNone(header.notes[0].lang)
        self.assertIsNone(header.notes[0].encoding)
        self.assertIsInstance(header.props[0], Prop)
        self.assertIsNone(header.props[0].lang)
        self.assertIsNone(header.props[0].encoding)
        self.assertEqual(header.props[0].type, elem.find("prop").get("type"))
        self.assertEqual(header.props[0].text, elem.find("prop").text)
        self.assertIsInstance(header.udes[0], Ude)
        self.assertEqual(header.udes[0].name, elem.find("ude").get("name"))
        self.assertEqual(header.udes[0].base, elem.find("ude").get("base"))
        self.assertEqual(len(header.udes[0].maps), 1)
        self.assertIsInstance(header.udes[0].maps[0], Map)
        self.assertEqual(
            header.udes[0].maps[0].unicode, elem.find("ude").find("map").get("unicode")
        )
        self.assertEqual(
            header.udes[0].maps[0].code, elem.find("ude").find("map").get("code")
        )
        self.assertEqual(
            header.udes[0].maps[0].ent, elem.find("ude").find("map").get("ent")
        )
        self.assertEqual(
            header.udes[0].maps[0].subst, elem.find("ude").find("map").get("subst")
        )

    def test_export_basic_header(self):
        header = header = Header(
            creationtool="creationtool",
            creationtoolversion="creationtoolversion",
            tmf="tmf",
            segtype="sentence",
            adminlang="adminlang",
            srclang="srclang",
            datatype="datatype",
            creationdate=datetime(2002, 1, 1, 16, 38, 12),
            creationid="creationid",
            changedate=datetime(2002, 4, 13, 2, 34, 1),
            changeid="changeid",
            encoding="encoding",
            notes=[Note(text="text")],
            props=[Prop(type="type", text="text")],
            udes=[
                Ude(
                    name="name",
                    base="base",
                    maps=[Map(unicode="unicode")],
                )
            ],
        )
        elem = header.to_element()
        for attr in header.__slots__:
            if attr == "_source_elem":
                continue
            elif attr in ("notes", "props", "udes"):
                continue
            elif attr in ("creationdate", "changedate"):
                self.assertEqual(
                    getattr(header, attr).strftime(r"%Y%m%dT%H%M%SZ"),
                    elem.get(attr),
                )
            elif attr in ("tmf", "encoding"):
                self.assertEqual(getattr(header, attr), elem.get(f"o-{attr}"))
            else:
                self.assertEqual(getattr(header, attr), elem.get(attr))
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(len(elem.findall("prop")), 1)
        self.assertEqual(len(elem.findall("ude")), 1)
        self.assertEqual(len(elem.find("ude").findall("map")), 1)
        self.assertEqual(elem.find("note").text, header.notes[0].text)
        self.assertEqual(elem.find("prop").get("type"), header.props[0].type)
        self.assertEqual(elem.find("prop").text, header.props[0].text)
        self.assertEqual(elem.find("ude").get("name"), header.udes[0].name)
        self.assertEqual(elem.find("ude").get("base"), header.udes[0].base)
        self.assertEqual(len(elem.find("ude").findall("map")), 1)
        self.assertEqual(
            elem.find("ude").find("map").get("unicode"), header.udes[0].maps[0].unicode
        )
        self.assertEqual(
            elem.find("ude").find("map").get("code"), header.udes[0].maps[0].code
        )
        self.assertEqual(
            elem.find("ude").find("map").get("ent"), header.udes[0].maps[0].ent
        )
        self.assertEqual(
            elem.find("ude").find("map").get("subst"), header.udes[0].maps[0].subst
        )

    def test_add_unknown_attributes(self):
        header = Header()
        with self.assertRaises(AttributeError):
            header.other = "test"

    def test_create_header_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<header other="other"/>""")
        new_header = Header(elem)
        self.assertNotIn("other", new_header.__dir__())
        self.assertEqual(new_header._source_elem, elem)

    def test_create_header_from_element_with_kwargs(self):
        elem = fromstring("""<header creationtool="creationtool" />""")
        header = Header(elem, creationtool="override creationtool")
        self.assertEqual(header._source_elem, elem)
        self.assertEqual(header.creationtool, "override creationtool")

    def test_use_header_dunder_methods(self):
        header = Header()
        header.creationtool = "header creationtool"
        self.assertEqual(header.creationtool, header["creationtool"])
        header["creationtool"] = "new creationtool"
        self.assertEqual(header["creationtool"], "new creationtool")
        with self.assertRaises(KeyError):
            header["unknown"]
        with self.assertRaises(KeyError):
            header["unknown"] = "test"
        del header["creationtool"]
        self.assertIsNone(header.creationtool)

    def test_create_header_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Header(fromstring("<wrong_tag/>"))
