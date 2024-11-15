"""
Tests for the Prop class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Prop


class TestProp(TestCase):
    def test_create_export_empty_prop(self):
        prop = Prop()
        for attr in prop.__slots__:
            if attr == "_source_elem":
                self.assertEqual(getattr(prop, attr), None)
            else:
                self.assertIsNone(getattr(prop, attr))

    def test_create_prop_from_element(self):
        elem = fromstring(
            """<prop xml:lang="en-US" o-encoding="utf-8" type="x-test">prop text</prop>"""
        )
        prop = Prop(elem)
        self.assertEqual(prop._source_elem, elem)
        self.assertEqual(
            prop.lang, elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.assertEqual(prop.encoding, elem.get("o-encoding"))
        self.assertEqual(prop.text, elem.text)
        self.assertEqual(prop.type, elem.get("type"))

    def test_export_basic_prop(self):
        prop = Prop(lang="en-US", encoding="utf-8", text="prop text", type="x-test")
        elem = prop.to_element()
        self.assertEqual(
            elem.get("{http://www.w3.org/XML/1998/namespace}lang"), prop.lang
        )
        self.assertEqual(elem.get("o-encoding"), prop.encoding)
        self.assertEqual(elem.text, prop.text)
        self.assertEqual(elem.get("type"), prop.type)

    def test_add_unknown_attributes(self):
        prop = Prop()
        with self.assertRaises(AttributeError):
            prop.other = "test"

    def test_create_prop_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<prop other="other"/>""")
        new_prop = Prop(elem)
        self.assertNotIn("other", new_prop.__dir__())

    def test_create_prop_from_element_with_kwargs(self):
        prop = Prop(fromstring("""<prop>text</prop>"""), text="override text")
        self.assertEqual(prop.text, "override text")

    def test_use_prop_dunder_methods(self):
        prop = Prop()
        prop.text = "text"
        self.assertEqual(prop.text, prop["text"])
        prop["text"] = "new text"
        self.assertEqual(prop["text"], "new text")
        with self.assertRaises(KeyError):
            prop["unknown"]
        with self.assertRaises(KeyError):
            prop["unknown"] = "test"
        del prop["type"]
        self.assertIsNone(prop.type)

    def test_create_prop_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Prop(fromstring("<wrong_tag/>"))
