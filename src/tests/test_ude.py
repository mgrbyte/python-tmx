"""
Tests for the Ude class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map, Ude


class TestUde(TestCase):
    def test_create_export_empty_ude(self):
        ude = Ude()
        self.assertIsNone(ude._source_elem)
        self.assertIsNone(ude.name)
        self.assertIsNone(ude.base)
        self.assertIsInstance(ude.maps, list)
        self.assertEqual(len(ude.maps), 0)
        with self.assertRaises(AttributeError):
            ude.to_element()

    def test_create_ude_from_element(self):
        elem = fromstring(
            """<ude name="ude name" base="ude base">
            <map unicode="#xF8FF 1" code="#xF0 1" ent="Apple_logo 1" subst="[Apple 1]"/>
            <map unicode="#xF8FF 2" code="#xF0 2" ent="Apple_logo 2" subst="[Apple 2]"/>
            </ude>"""
        )
        ude = Ude(elem)
        self.assertEqual(ude._source_elem, elem)
        self.assertEqual(ude.name, elem.get("name"))
        self.assertEqual(ude.base, elem.get("base"))
        self.assertEqual(len(ude.maps), 2)
        for index, item in enumerate(ude.maps):
            self.assertIsInstance(item, Map)
            self.assertEqual(item.unicode, elem[index].get("unicode"))
            self.assertEqual(item.code, elem[index].get("code"))
            self.assertEqual(item.ent, elem[index].get("ent"))
            self.assertEqual(item.subst, elem[index].get("subst"))

    def test_export_basic_ude(self):
        ude = Ude(
            name="ude name", base="ude base", maps=[Map(unicode="1"), Map(unicode="2")]
        )
        elem = ude.to_element()
        self.assertEqual(elem.get("name"), ude.name)
        self.assertEqual(elem.get("base"), ude.base)
        self.assertEqual(len(elem), 2)
        self.assertEqual(elem[0].get("unicode"), ude.maps[0].unicode)
        self.assertEqual(elem[1].get("unicode"), ude.maps[1].unicode)

    def test_export_ude_no_base_no_maps_with_code(self):
        ude = Ude(
            name="ude name",
            base="ude base",
            maps=[Map(unicode=f"{x}") for x in range(10)],
        )
        elem = ude.to_element()
        self.assertEqual(elem.get("name"), ude.name)
        self.assertEqual(elem.get("base"), ude.base)
        self.assertEqual(len(elem), 10)

    def test_export_ude_no_base_with_maps_with_code(self):
        ude = Ude(
            name="ude name",
            maps=[Map(unicode="1", code="2"), Map(unicode="3", code="4")],
        )
        with self.assertRaises(AttributeError):
            ude.to_element()

    def test_export_ude_no_name(self):
        ude = Ude(base="ude base", maps=[Map(unicode="1"), Map(unicode="2")])
        with self.assertRaises(AttributeError):
            ude.to_element()

    def test_add_unknown_attributes(self):
        ude = Ude()
        with self.assertRaises(AttributeError):
            ude.other = "test"

    def test_create_ude_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<ude other="other"/>""")
        new_ude = Ude(elem)
        self.assertNotIn("other", new_ude.__dir__())
        self.assertEqual(new_ude._source_elem, elem)

    def test_create_ude_from_element_with_kwargs(self):
        elem = fromstring(
            """<ude base="ude base">
            <map unicode="#xF8FF 1" code="#xF0 1" ent="Apple_logo 1" subst="[Apple 1]"/>
            <map unicode="#xF8FF 2" code="#xF0 2" ent="Apple_logo 2" subst="[Apple 2]"/>
            </ude>"""
        )
        ude = Ude(elem, name="override name")
        self.assertEqual(ude._source_elem, elem)
        self.assertEqual(ude.name, "override name")
        self.assertEqual(ude.base, "ude base")

    def test_use_ude_dunder_methods(self):
        ude = Ude()
        ude.name = "ude name"
        self.assertEqual(ude.name, ude["name"])
        ude["name"] = "new name"
        self.assertEqual(ude["name"], "new name")
        with self.assertRaises(KeyError):
            ude["unknown"]
        with self.assertRaises(KeyError):
            ude["unknown"] = "test"
        del ude["name"]
        self.assertIsNone(ude.name)

    def test_create_ude_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Ude(fromstring("<wrong_tag/>"))
