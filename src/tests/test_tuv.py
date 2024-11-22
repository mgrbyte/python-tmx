from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.inline import Bpt, Ept, Ph
from PythonTmx.structural import Note, Prop, Tuv


class TestTuv(TestCase):
    def test_create_export_empty_tuv(self):
        tuv = Tuv()
        for attr in tuv.__slots__:
            match attr:
                case "notes" | "props" | "segment":
                    self.assertIsInstance(getattr(tuv, attr), list)
                    self.assertEqual(len(getattr(tuv, attr)), 0)
                case _:
                    self.assertIsNone(getattr(tuv, attr))
        with self.assertRaises(AttributeError):
            tuv.to_element()

    def create_tuv_from_element(self):
        elem = fromstring(
            """<tuv xml:lang="en-US"
        o-encoding="utf-8"
        datatype="PlainText"
        usagecount="1"
        lastusagedate="20241122T162345Z"
        creationtool="PythonTmx Test Suite"
        creationtoolversion="0.3"
        creationdate="20241122T162345Z"
        creationid="Enzo"
        changedate="20241122T162345Z"
        changeid="DJ Khaled"
        o-tmf="xml string">
            <seg>This is a test</seg>
            <prop type="x-tmx-tuv-comment">This is a comment</prop>
            <note>This is a note</note>
        </tuv>
        """
        )
        tuv = Tuv(elem)
        for attr in tuv.__slots__:
            val = getattr(tuv, attr)
            match attr:
                case "_source_elem":
                    self.assertEqual(val, elem)
                case "creationdate" | "changedate" | "lastusagedate":
                    self.assertEqual(val.strftime(r"%Y%m%dT%H%M%SZ"), elem.get(attr))
                case "notes":
                    self.assertIsInstance(tuv.notes, list)
                    self.assertEqual(len(tuv.notes), len(elem.findall("note")))
                    self.assertEqual(tuv.notes[0].text, elem.find("note").text)
                case "props":
                    self.assertIsInstance(tuv.props, list)
                    self.assertEqual(len(tuv.props), len(elem.findall("prop")))
                    self.assertEqual(tuv.props[0].text, elem.find("prop").text)
                    self.assertEqual(tuv.props[0].type, elem.find("prop").get("type"))
                case "segment":
                    self.assertEqual(val, elem.find("seg").text)
                case "lang":
                    self.assertEqual(
                        val, elem.get("{http://www.w3.org/XML/1998/namespace}lang")
                    )
                case _:
                    self.assertEqual(val, elem.get(attr))

    def test_export_minimal_tuv(self):
        tuv = Tuv(lang="en-US")
        elem = tuv.to_element()
        self.assertEqual(elem.tag, "tuv")
        self.assertEqual(
            elem.get("{http://www.w3.org/XML/1998/namespace}lang"), "en-US"
        )
        self.assertEqual(len(elem), 1)

    def test_add_unknown_attribute(self):
        tuv = Tuv()
        with self.assertRaises(AttributeError):
            tuv.unknown = "test"

    def test_create_tuv_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<tuv other="other"/>""")
        new_tuv = Tuv(elem)
        self.assertNotIn("other", new_tuv.__dir__())
        self.assertEqual(new_tuv._source_elem, elem)

    def test_create_tuv_from_element_with_kwargs(self):
        elem = fromstring(
            """<tuv creationtool="creationtool" creationtoolversion="1.0" />"""
        )
        tuv = Tuv(elem, creationtool="override creationtool")
        self.assertEqual(tuv._source_elem, elem)
        self.assertEqual(tuv.creationtool, "override creationtool")
        self.assertEqual(tuv.creationtoolversion, "1.0")

    def test_export_tuv_with_mixed_segment(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "This is the text of the seg",
                Ph(content="This is the text of the ph", i=1),
                "This is the tail of the ph",
            ],
        )
        elem = tuv.to_element()
        self.assertEqual(elem.tag, "tuv")
        self.assertEqual(len(elem), 1)
        self.assertEqual(len(elem.attrib), 1)
        seg = elem.find("seg")
        self.assertEqual(seg.text, "This is the text of the seg")
        self.assertEqual(seg.find("ph").text, "This is the text of the ph")
        self.assertEqual(seg.find("ph").get("i"), "1")
        self.assertEqual(seg.find("ph").tail, "This is the tail of the ph")

    def test_export_tuv_only_inline_segment(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                Ph(content="This is the text of the first ph", i=1),
                Ph(content="This is the text of the second ph", i=2),
            ],
        )
        elem = tuv.to_element()
        self.assertEqual(elem.tag, "tuv")
        self.assertEqual(len(elem), 1)
        seg = elem.find("seg")
        self.assertEqual(len(seg), 2)
        self.assertEqual(seg.text, "")
        self.assertEqual(seg[0].text, "This is the text of the first ph")
        self.assertEqual(seg[1].text, "This is the text of the second ph")
        self.assertEqual(seg[0].get("i"), "1")
        self.assertEqual(seg[1].get("i"), "2")

    def test_export_tuv_no_ept(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Bpt(content="This is the text of the only bpt", i=1),
                "tail of the bpt",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0], "Ept with i=None is missing its corresponding Bpt"
        )

    def test_export_tuv_no_bpt(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Ept(content="This is the text of the only ept", i=1),
                "tail of the ept",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0], "Ept with i=1 is missing its corresponding Bpt"
        )

    def test_export_tuv_too_many_bpt(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Bpt(content="This is the text of the first bpt", i=1),
                Bpt(content="This is the text of the second bpt", i=2),
                Ept(content="This is the text of the ept", i=1),
                "tail of the bpt",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0],
            "Ept with i=None is missing its corresponding Bpt",
        )

    def test_export_tuv_too_many_ept(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Bpt(content="This is the text of the first bpt", i=1),
                Ept(content="This is the text of the second ept", i=1),
                Ept(content="This is the text of the third ept", i=2),
                "tail of the bpt",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0],
            "Ept with i=2 is missing its corresponding Bpt",
        )

    def test_export_tuv_repeated_bpt_i(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Bpt(content="This is the text of the first bpt", i=1),
                Bpt(content="This is the text of the second bpt", i=1),
                Ept(content="This is the text of the ept", i=1),
                "tail of the bpt",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0],
            "Duplicate Bpt with i=1 at index: 2",
        )

    def test_export_tuv_repeated_ept_i(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "text of the first seg",
                Bpt(content="This is the text of the first bpt", i=1),
                Ept(content="This is the text of the second ept", i=1),
                Ept(content="This is the text of the third ept", i=1),
                "tail of the bpt",
            ],
        )
        with self.assertRaises(ValueError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0],
            "Duplicate Ept with i=1 at index: 3",
        )

    def test_export_tuv_not_inline_segment(self):
        tuv = Tuv(
            lang="en-US",
            segment=[
                "This is the text of the first seg",
                123,
                "tail of the bpt",
            ],
        )
        with self.assertRaises(TypeError) as cm:
            tuv.to_element()
        self.assertEqual(
            cm.exception.args[0],
            "Invalid item in segment:\ntype: int\nvalue: 123\nindex: 1",
        )

    def test_use_tuv_dunder_methods(self):
        tuv = Tuv()
        tuv.creationtool = "creationtool"
        self.assertEqual(tuv.creationtool, tuv["creationtool"])
        tuv["creationtool"] = "new creationtool"
        self.assertEqual(tuv["creationtool"], "new creationtool")
        with self.assertRaises(KeyError):
            tuv["unknown"]
        with self.assertRaises(KeyError):
            tuv["unknown"] = "test"
        del tuv["creationtool"]
        self.assertIsNone(tuv.creationtool)
        tuv.notes = [Note(text=str(x)) for x in range(10)]
        for i in tuv.notes:
            self.assertIsInstance(i, Note)

    def test_create_tuv_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Tuv(fromstring("<wrong_tag/>"))

    def test_export_tuv_wrong_attribute_type(self):
        tuv = Tuv(
            lang="en-us",
        )
        tuv.creationtool = 123
        with self.assertRaises(TypeError):
            tuv.to_element()

    def test_export_tuv_any_iterable(self):
        tuv = Tuv(lang="en-US")

        # list
        tuv.notes = [Note(text="note")]
        # tuple
        tuv.segment = ("first ", "second")
        # set
        tuv.props = {Prop(text="prop", type="x-test")}

        elem = tuv.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(len(elem.findall("seg")), 1)
        self.assertEqual(len(elem.findall("prop")), 1)
        self.assertEqual(elem.find("seg").text, "first second")
        self.assertEqual(elem.find("note").text, "note")
        self.assertEqual(elem.find("prop").text, "prop")
        self.assertEqual(elem.find("prop").get("type"), "x-test")

        # Dict Value
        tuv.notes = {1: Note(text="text")}.values()
        elem = tuv.to_element()
        self.assertEqual(len(elem.findall("note")), 1)
        self.assertEqual(elem.find("note").text, "text")
