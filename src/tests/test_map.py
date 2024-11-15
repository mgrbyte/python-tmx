"""
Tests for the Map class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map


class TestMap(TestCase):
    def test_create_export_empty_map(self):
        map = Map()
        for attr in map.__slots__:
            if attr == "_source_elem":
                self.assertEqual(getattr(map, attr), None)
            else:
                self.assertIsNone(getattr(map, attr))

    def test_create_map_from_element(self):
        elem = fromstring(
            """<map unicode="#xF8FF" code="#xF0" ent="Apple_logo" subst="[Apple]"/>"""
        )
        map = Map(elem)
        for attr in map.__slots__:
            if attr == "_source_elem":
                self.assertEqual(getattr(map, attr), elem)
            else:
                self.assertEqual(getattr(map, attr), elem.get(attr))

    def test_export_basic_map(self):
        map = Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]")
        elem = map.to_element()
        for attr in map.__slots__:
            if attr == "_source_elem":
                self.assertEqual(getattr(map, attr), elem)
            else:
                self.assertEqual(getattr(map, attr), elem.get(attr))

    def test_add_unknown_attributes(self):
        map = Map()
        with self.assertRaises(AttributeError):
            map.other = "test"

    def test_create_map_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<map other="other"/>""")
        new_map = Map(elem)
        self.assertNotIn("other", new_map.__dir__())

    def test_create_map_from_element_with_kwargs(self):
        map = Map(
            fromstring("""<map unicode="#xF8FF" />"""), unicode="override unicode"
        )
        self.assertEqual(map.unicode, "override unicode")

    def test_use_map_dunder_methods(self):
        map = Map()
        map.unicode = "#xF8FF"
        self.assertEqual(map.unicode, map["unicode"])
        map["unicode"] = "new unicode"
        self.assertEqual(map["unicode"], "new unicode")
        with self.assertRaises(KeyError):
            map["unknown"]
        with self.assertRaises(KeyError):
            map["unknown"] = "test"
        del map["unicode"]
        self.assertIsNone(map.unicode)

    def test_create_map_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Map(fromstring("<wrong_tag/>"))
