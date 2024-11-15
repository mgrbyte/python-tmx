"""
Tests for the Prop class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Prop


class TestProp(TestCase):
    def test_empty_prop(self):
        prop = Prop()
        self.assertIsNone(prop._source_elem)
        self.assertIsNone(prop.lang)
        self.assertIsNone(prop.encoding)
        self.assertIsNone(prop.text)
        with self.assertRaises(AttributeError):
            prop.to_element()

    def test_prop_from_element(self):
        elem = fromstring(
            """<prop type="type" xml:lang="lang" o-encoding="encoding">text</prop>"""
        )
        prop = Prop(elem)
        self.assertEqual(prop._source_elem, elem)
        self.assertEqual(
            prop.lang, elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.assertEqual(prop.encoding, elem.get("o-encoding"))
        self.assertEqual(prop.type, elem.get("type"))
        self.assertEqual(prop.text, elem.text)
        new_elem = prop.to_element()
        self.assertEqual(
            new_elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
            elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
        )
        self.assertEqual(new_elem.get("o-encoding"), elem.get("o-encoding"))
        self.assertEqual(new_elem.text, elem.text)

    def test_unknown_attributes(self):
        prop = Prop()
        with self.assertRaises(AttributeError):
            prop.other = "test"
        self.assertIsNone(prop._source_elem)
        self.assertIsNone(prop.lang)
        self.assertIsNone(prop.encoding)
        self.assertIsNone(prop.type)
        self.assertIsNone(prop.text)

        elem = fromstring("""<prop other="other"/>""")
        new_prop = Prop(elem)
        self.assertNotIn("other", new_prop.__dir__())
        self.assertEqual(new_prop._source_elem, elem)
        self.assertIsNone(new_prop.lang)
        self.assertIsNone(new_prop.encoding)
        self.assertIsNone(prop.type)
        self.assertIsNone(new_prop.text)

        prop.text = 1337
        with self.assertRaises(TypeError):
            prop.to_element()
        prop.text = None
        with self.assertRaises(AttributeError):
            prop.to_element()

    def test_create_prop_from_element_with_kwargs(self):
        elem = fromstring("""<prop type="type" o-encoding="encoding">text</prop>""")
        prop = Prop(elem, lang="override lang", encoding="override encoding")
        self.assertEqual(prop._source_elem, elem)
        self.assertEqual(prop.lang, "override lang")
        self.assertEqual(prop.encoding, "override encoding")
        self.assertEqual(prop.type, elem.get("type"))
        self.assertEqual(prop.text, elem.text)
