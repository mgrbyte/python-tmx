from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map


class TestMap(TestCase):
  def test_create_export_empty_map(self):
    map = Map()
    for attr in map.__slots__:
      self.assertIsNone(getattr(map, attr))
    with self.assertRaises(AttributeError):
      map.to_element()

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

  def test_export_minimal_map(self):
    map = Map(unicode="#xF8FF")
    elem = map.to_element()
    self.assertEqual(elem.get("unicode"), "#xF8FF")
    self.assertEqual(elem.tag, "map")
    self.assertEqual(len(elem), 0)
    self.assertEqual(len(elem.attrib), 1)

  def test_add_unknown_attributes(self):
    map = Map()
    with self.assertRaises(AttributeError):
      map.other = "test"

  def test_create_map_from_element_with_unknwon_attributes(self):
    elem = fromstring("""<map other="other"/>""")
    new_map = Map(elem)
    self.assertNotIn("other", new_map.__dir__())

  def test_create_map_from_element_with_kwargs(self):
    map = Map(fromstring("""<map unicode="#xF8FF" />"""), unicode="override unicode")
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

  def test_export_map_wrong_attribute_type(self):
    map = Map()
    map.unicode = 123
    with self.assertRaises(TypeError):
      map.to_element()

  def test_export_full_map(self):
    map = Map(
      unicode="unicode",
      code="code",
      ent="ent",
      subst="subst",
    )
    elem = map.to_element()
    self.assertEqual(elem.get("unicode"), "unicode")
    self.assertEqual(elem.get("code"), "code")
    self.assertEqual(elem.get("ent"), "ent")
    self.assertEqual(elem.get("subst"), "subst")
    self.assertEqual(elem.tag, "map")
    self.assertEqual(len(elem), 0)
    self.assertEqual(len(elem.attrib), 4)
