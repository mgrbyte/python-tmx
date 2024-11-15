"""
Tests for the Ude class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map, Ude


class TestUde(TestCase):
    def test_empty_ude(self):
        ude = Ude()
        self.assertIsNone(ude._source_elem)
        self.assertIsNone(ude.name)
        self.assertIsNone(ude.base)
        self.assertIsInstance(ude.maps, list)
        self.assertEqual(len(ude.maps), 0)
        with self.assertRaises(AttributeError):
            ude.to_element()

    def test_ude_from_element(self):
        elem = fromstring(
            """<ude name="ude name" base="ude base">
            <map unicode="#xF8FF 1" code="#xF0 1" ent="Apple_logo 1" subst="[Apple 1]"/>
            <map unicode="#xF8FF 2" code="#xF0 2" ent="Apple_logo 2" subst="[Apple 2]"/>
            </ude>"""
        )
        ude = Ude(elem)
        self.assertEqual(ude._source_elem, elem)

    def test_unknown_attributes(self):
        ude = Ude()
        with self.assertRaises(AttributeError):
            ude.other = "test"

        elem = fromstring("""<ude other="other"/>""")
        new_ude = Ude(elem)
        self.assertNotIn("other", new_ude.__dir__())
        self.assertEqual(new_ude._source_elem, elem)
        self.assertIsNone(new_ude.name)
        self.assertIsNone(new_ude.base)
        self.assertIsInstance(new_ude.maps, list)
        self.assertEqual(len(new_ude.maps), 0)

    def test_create_ude_from_element_with_kwargs(self):
        elem = fromstring(
            """<ude base="ude base">
            <map unicode="#xF8FF 1" code="#xF0 1" ent="Apple_logo 1" subst="[Apple 1]"/>
            <map unicode="#xF8FF 2" code="#xF0 2" ent="Apple_logo 2" subst="[Apple 2]"/>
            </ude>"""
        )
        ude = Ude(elem, name="override name", base="override base")
        self.assertEqual(ude._source_elem, elem)
        self.assertEqual(ude.name, "override name")
        self.assertEqual(ude.base, "override base")
        self.assertEqual(len(ude.maps), 2)
        self.assertIsInstance(ude.maps, list)
        self.assertIsInstance(ude.maps[0], Map)
        self.assertEqual(ude.maps[0].unicode, elem[0].get("unicode"))
        self.assertEqual(ude.maps[0].code, elem[0].get("code"))
        self.assertEqual(ude.maps[0].ent, elem[0].get("ent"))
        self.assertEqual(ude.maps[0].subst, elem[0].get("subst"))
        self.assertIsInstance(ude.maps[1], Map)
        self.assertEqual(ude.maps[1].unicode, elem[1].get("unicode"))
        self.assertEqual(ude.maps[1].code, elem[1].get("code"))
        self.assertEqual(ude.maps[1].ent, elem[1].get("ent"))
        self.assertEqual(ude.maps[1].subst, elem[1].get("subst"))
