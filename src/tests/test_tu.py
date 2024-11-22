from datetime import datetime
from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Note, Prop, Tu, Tuv


class TestTu(TestCase):
    def test_create_export_empty_tu(self):
        tu = Tu()
        for attr in tu.__slots__:
            match attr:
                case "notes" | "props" | "tuvs":
                    self.assertIsInstance(getattr(tu, attr), list)
                    self.assertEqual(len(getattr(tu, attr)), 0)
                case _:
                    self.assertIsNone(getattr(tu, attr))
        with self.assertRaises(ValueError):
            tu.to_element()

    def test_create_tu_from_element(self):
        elem = fromstring(
            """<tu tuid="coolid"
                o-encoding="utf-8"
                datatype="Plaintext"
                usagecount="12"
                lastusagedate="20241120T120000Z"
                creationtool="PythonTmx Test Suite"
                creationtoolversion="0.3"
                creationdate="20221120T120000Z"
                creationid="PythonTmx"
                changedate="20241120T120000Z"
                segtype="sentence"
                changeid="Testing"
                o-tmf="testing"
                srclang="en-us">
              <tuv xml:lang="en-US">
                <seg>Potatoes</seg>
              </tuv>
              <prop type="Domain">Cooking</prop>
              <tuv xml:lang="fr-CA">
                <seg>Pomme de terre</seg>
              </tuv>
              <tuv xml:lang="de-DE">
                <seg>Kartoffel</seg>
              </tuv>
              <note>This is a note</note>
              </tu>"""
        )
        tu = Tu(elem)
        for attr in tu.__slots__:
            val = getattr(tu, attr)
            match attr:
                case "_source_elem":
                    self.assertEqual(val, elem)
                case "encoding" | "tmf":
                    self.assertEqual(val, elem.get(f"o-{attr}"))
                case "creationdate" | "changedate" | "lastusagedate":
                    self.assertEqual(val.strftime(r"%Y%m%dT%H%M%SZ"), elem.get(attr))
                case "notes":
                    self.assertIsInstance(tu.notes, list)
                    self.assertEqual(len(tu.notes), len(elem.findall("note")))
                    self.assertEqual(tu.notes[0].text, elem.find("note").text)
                case "props":
                    self.assertIsInstance(tu.props, list)
                    self.assertEqual(len(tu.props), len(elem.findall("prop")))
                    self.assertEqual(tu.props[0].text, elem.find("prop").text)
                    self.assertEqual(tu.props[0].type, elem.find("prop").get("type"))
                case "tuvs":
                    self.assertIsInstance(tu.tuvs, list)
                    self.assertEqual(len(tu.tuvs), len(elem.findall("tuv")))
                    tuvs = elem.findall("tuv")
                    for i in range(len(tu.tuvs)):
                        self.assertEqual(
                            tu.tuvs[i].lang,
                            tuvs[i].get("{http://www.w3.org/XML/1998/namespace}lang"),
                        )
                        self.assertEqual(tu.tuvs[i].segment, tuvs[i].find("seg").text)
                case "creationdate" | "changedate" | "lastusagedate":
                    self.assertIsInstance(val, datetime)
                    self.assertEqual(
                        val.strftime(r"%Y%m%dT%H%M%SZ"),
                        elem.get(attr),
                    )
                case "usagecount":
                    self.assertIsInstance(val, int)
                    self.assertEqual(int(elem.get(attr)), val)
                case _:
                    self.assertEqual(val, elem.get(attr))

    def test_export_minimal_tu(self):
        tu = Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")])
        elem = tu.to_element()
        self.assertEqual(
            elem.tag,
            "tu",
        )
        self.assertEqual(len(elem.findall("tuv")), len(tu.tuvs))
        self.assertEqual(
            elem.find("tuv").get("{http://www.w3.org/XML/1998/namespace}lang"), "en-US"
        )
        self.assertEqual(elem.find("tuv").find("seg").text, "Potatoes")

    def test_add_unknown_attributes(self):
        tu = Tu()
        with self.assertRaises(AttributeError):
            tu.other = "test"

    def test_create_tu_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<tu other="other"/>""")
        new_tu = Tu(elem)
        self.assertNotIn("other", new_tu.__dir__())
        self.assertEqual(new_tu._source_elem, elem)

    def test_create_tu_from_element_with_kwargs(self):
        elem = fromstring(
            """<tu creationtool="creationtool" creationtoolversion="1.0" />"""
        )
        tu = Tu(elem, creationtool="override creationtool")
        self.assertEqual(tu._source_elem, elem)
        self.assertEqual(tu.creationtool, "override creationtool")
        self.assertEqual(tu.creationtoolversion, "1.0")

    def test_use_tu_dunder_methods(self):
        tu = Tu()
        tu.creationtool = "creationtool"
        self.assertEqual(tu.creationtool, tu["creationtool"])
        tu["creationtool"] = "new creationtool"
        self.assertEqual(tu["creationtool"], "new creationtool")
        with self.assertRaises(KeyError):
            tu["unknown"]
        with self.assertRaises(KeyError):
            tu["unknown"] = "test"
        del tu["creationtool"]
        self.assertIsNone(tu.creationtool)
        tu.notes = [Note(text=str(x)) for x in range(10)]
        for i in tu.notes:
            self.assertIsInstance(i, Note)

    def test_create_tu_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Tu(fromstring("<wrong_tag/>"))

    def test_export_tu_wrong_attribute_type(self):
        tu = Tu(creationtool=1, tuvs=[Tu()])
        tu.creationtool = 123
        with self.assertRaises(TypeError):
            tu.to_element()

    def test_export_tu_any_iterable(self):
        tu = Tu()

        # list
        tu.notes = [Note(text="note")]
        # tuple
        tu.tuvs = (Tuv(lang="en-US"),)
        # set
        tu.props = {Prop(text="prop", type="x-test")}

        elem = tu.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(len(elem.findall("tuv")), 1)
        self.assertEqual(len(elem.findall("prop")), 1)
        self.assertEqual(elem.find("tuv").find("seg").text, "")
        self.assertEqual(elem.find("note").text, "note")
        self.assertEqual(elem.find("prop").text, "prop")
        self.assertEqual(elem.find("prop").get("type"), "x-test")

        # Dict Value
        tu.notes = {1: Note(text="text")}.values()
        elem = tu.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(elem.find("note").text, "text")
