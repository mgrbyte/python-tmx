from datetime import datetime
from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Header, Note, Prop, Ude


class TestHeader(TestCase):
    def test_create_export_empty_header(self):
        header = Header()
        for attr in header.__slots__:
            match attr:
                case "udes" | "props" | "notes":
                    self.assertIsInstance(getattr(header, attr), list)
                    self.assertEqual(len(getattr(header, attr)), 0)
                case _:
                    self.assertIsNone(getattr(header, attr))
        with self.assertRaises(AttributeError):
            header.to_element()

    def test_create_header_from_element(self):
        elem = fromstring(
            """<header creationtool="PythonTmx" creationtoolversion="0.3" 
            datatype="PlainText" segtype="sentence" adminlang="en-us"
            srclang="en-US" o-tmf="xml string" creationdate="20241119T162345Z"
            creationid="Enzo" changedate="20241120T155800Z" changeid="DJ Khaled"
            o-encoding="utf-8">
                <prop type="x-tmx-header-comment">This is a comment</prop>
                <note>This is a note</note>
                <ude name="ude name" base="ude base">
                    <map unicode="unicode" code="code" ent="ent" subst="subst"/>
                </ude>
            </header>
            """
        )
        header = Header(elem)
        for attr in header.__slots__:
            val = getattr(header, attr)
            match attr:
                case "_source_elem":
                    self.assertEqual(val, elem)
                case "encoding" | "tmf":
                    self.assertEqual(val, elem.get(f"o-{attr}"))
                case "creationdate" | "changedate" | "lastusagedate":
                    self.assertEqual(val.strftime(r"%Y%m%dT%H%M%SZ"), elem.get(attr))
                case "notes":
                    self.assertIsInstance(header.notes, list)
                    self.assertEqual(len(header.notes), len(elem.findall("note")))
                    self.assertEqual(header.notes[0].text, elem.find("note").text)
                case "props":
                    self.assertIsInstance(header.props, list)
                    self.assertEqual(len(header.props), len(elem.findall("prop")))
                    self.assertEqual(header.props[0].text, elem.find("prop").text)
                    self.assertEqual(
                        header.props[0].type, elem.find("prop").get("type")
                    )
                case "udes":
                    self.assertIsInstance(header.udes, list)
                    self.assertEqual(len(header.udes), len(elem.findall("ude")))
                    self.assertEqual(header.udes[0].name, elem.find("ude").get("name"))
                    self.assertEqual(header.udes[0].base, elem.find("ude").get("base"))
                    self.assertEqual(
                        len(header.udes[0].maps), len(elem.find("ude").findall("map"))
                    )
                    self.assertEqual(
                        header.udes[0].maps[0].unicode,
                        elem.find("ude").find("map").get("unicode"),
                    )
                    self.assertEqual(
                        header.udes[0].maps[0].code,
                        elem.find("ude").find("map").get("code"),
                    )
                    self.assertEqual(
                        header.udes[0].maps[0].ent,
                        elem.find("ude").find("map").get("ent"),
                    )
                    self.assertEqual(
                        header.udes[0].maps[0].subst,
                        elem.find("ude").find("map").get("subst"),
                    )
                case "creationdate" | "changedate" | "lastusagedate":
                    self.assertIsInstance(val, datetime)
                    self.assertEqual(
                        val.strftime(r"%Y%m%dT%H%M%SZ"),
                        elem.get(attr),
                    )
                case _:
                    self.assertEqual(val, elem.get(attr))

    def test_export_minimal_header(self):
        header = Header(
            creationtool="creationtool",
            creationtoolversion="1.0",
            segtype="sentence",
            tmf="tmf",
            adminlang="en-us",
            srclang="en-US",
            datatype="PlainText",
            encoding="utf-8",
        )
        elem = header.to_element()
        for attr in (
            "creationtool",
            "creationtoolversion",
            "segtype",
            "adminlang",
            "srclang",
            "datatype",
        ):
            self.assertEqual(elem.get(attr), getattr(header, attr))
        self.assertEqual(elem.get("o-tmf"), header.tmf)
        self.assertEqual(elem.get("o-encoding"), header.encoding)

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
        elem = fromstring(
            """<header creationtool="creationtool" creationtoolversion="1.0" />"""
        )
        header = Header(elem, creationtool="override creationtool")
        self.assertEqual(header._source_elem, elem)
        self.assertEqual(header.creationtool, "override creationtool")
        self.assertEqual(header.creationtoolversion, "1.0")

    def test_use_header_dunder_methods(self):
        header = Header()
        header.creationtool = "creationtool"
        self.assertEqual(header.creationtool, header["creationtool"])
        header["creationtool"] = "new creationtool"
        self.assertEqual(header["creationtool"], "new creationtool")
        with self.assertRaises(KeyError):
            header["unknown"]
        with self.assertRaises(KeyError):
            header["unknown"] = "test"
        del header["creationtool"]
        self.assertIsNone(header.creationtool)
        header.notes = [Note(text=str(x)) for x in range(10)]
        for i in header.notes:
            self.assertIsInstance(i, Note)

    def test_create_header_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Header(fromstring("<wrong_tag/>"))

    def test_export_header_wrong_attribute_type(self):
        header = Header(
            creationtool="creationtool",
            creationtoolversion="1.0",
            segtype="sentence",
            tmf="tmf",
            adminlang="en-us",
            srclang="en-US",
            datatype="PlainText",
            encoding="utf-8",
        )
        header.creationtool = 123
        with self.assertRaises(TypeError):
            header.to_element()

    def test_export_header_any_iterable(self):
        header = Header(
            creationtool="creationtool",
            creationtoolversion="1.0",
            segtype="sentence",
            tmf="tmf",
            adminlang="en-us",
            srclang="en-US",
            datatype="PlainText",
            encoding="utf-8",
        )

        # list
        header.notes = [Note(text="note")]
        # tuple
        header.props = (Prop(text="prop", type="x-test"),)
        # set
        header.udes = {Ude(name="ude")}

        elem = header.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(len(elem.findall("prop")), 1)
        self.assertEqual(len(elem.findall("ude")), 1)
        self.assertEqual(elem.find("note").text, "note")
        self.assertEqual(elem.find("prop").text, "prop")
        self.assertEqual(elem.find("prop").get("type"), "x-test")
        self.assertEqual(elem.find("ude").attrib["name"], "ude")

        # Dict Value
        header.notes = {1: Note(text="text")}.values()
        elem = header.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(elem.find("note").text, "text")
