"""
Tests for the Map class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map


class TestMap(TestCase):
    def test_empty_map(self):
        map = Map()
        self.assertIsNone(map._source_elem)
        self.assertIsNone(map.unicode)
        self.assertIsNone(map.code)
        self.assertIsNone(map.ent)
        self.assertIsNone(map.subst)
        with self.assertRaises(AttributeError):
            map.to_element()

    def test_map_from_element(self):
        elem = fromstring(
            """<map unicode="#xF8FF" code="#xF0" ent="Apple_logo" subst="[Apple]"/>"""
        )
        map = Map(elem)
        self.assertEqual(map._source_elem, elem)
        self.assertEqual(map.unicode, elem.get("unicode"))
        self.assertEqual(map.code, elem.get("code"))
        self.assertEqual(map.ent, elem.get("ent"))
        self.assertEqual(map.subst, elem.get("subst"))
        new_elem = map.to_element()
        self.assertEqual(new_elem.get("unicode"), elem.get("unicode"))
        self.assertEqual(new_elem.get("code"), elem.get("code"))
        self.assertEqual(new_elem.get("ent"), elem.get("ent"))
        self.assertEqual(new_elem.get("subst"), elem.get("subst"))

    def test_unknown_attributes(self):
        map = Map()
        with self.assertRaises(AttributeError):
            map.other = "test"

        elem = fromstring("""<map other="other"/>""")
        new_map = Map(elem)
        self.assertNotIn("other", new_map.__dir__())
        self.assertEqual(new_map._source_elem, elem)
        self.assertIsNone(new_map.unicode)
        self.assertIsNone(new_map.code)
        self.assertIsNone(new_map.ent)
        self.assertIsNone(new_map.subst)
        map.unicode = 1337
        with self.assertRaises(TypeError):
            map.to_element()
        map.unicode = None
        with self.assertRaises(AttributeError):
            map.to_element()

    def test_create_map_from_element_with_kwargs(self):
        elem = fromstring("""<map ent="Apple_logo" subst="[Apple]"/>""")
        map = Map(elem, unicode="#xF8FF", code=123, ent="override ent")
        self.assertEqual(map._source_elem, elem)
        self.assertEqual(map.unicode, "#xF8FF")
        self.assertEqual(map.code, 123)
        self.assertEqual(map.ent, "override ent")
        self.assertEqual(map.subst, "[Apple]")
