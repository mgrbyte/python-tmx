from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Map, Ude


class TestUde(TestCase):
  def test_create_export_empty_ude(self):
    ude = Ude()
    for attr in ude.__slots__:
      match attr:
        case "maps":
          self.assertIsInstance(getattr(ude, attr), list)
          self.assertEqual(len(getattr(ude, attr)), 0)
        case _:
          self.assertIsNone(getattr(ude, attr))
    with self.assertRaises(AttributeError):
      ude.to_element()

  def test_create_ude_from_element(self):
    elem = fromstring(
      """<ude name="name" base="base">
            <map unicode="unicode 1" code="code 1" ent="ent 1" subst="subst 1"/>
            <map unicode="unicode 2" code="code 2" ent="ent 2" subst="subst 2"/>
            </ude>"""
    )
    ude = Ude(elem)
    self.assertEqual(ude._source_elem, elem)
    self.assertEqual(ude.name, elem.get("name"))
    self.assertEqual(ude.base, elem.get("base"))
    self.assertEqual(len(ude.maps), 2)
    for index, item in enumerate(ude.maps):
      self.assertIsInstance(item, Map)
      for attr in item.__slots__:
        match attr:
          case "_source_elem":
            self.assertEqual(item._source_elem, elem[index])
          case _:
            self.assertEqual(getattr(item, attr), elem[index].get(attr))

  def test_export_minimal_ude(self):
    ude = Ude(name="ude name")
    elem = ude.to_element()
    self.assertEqual(elem.get("name"), ude.name)
    self.assertEqual(elem.tag, "ude")
    self.assertEqual(len(elem), 0)
    self.assertEqual(len(elem.attrib), 1)

  def test_export_ude_no_base_no_maps_with_code(self):
    ude = Ude(
      name="ude name",
      maps=[Map(unicode=f"{x}") for x in range(10)],
    )
    elem = ude.to_element()
    self.assertEqual(elem.get("name"), ude.name)
    self.assertEqual(len(elem), 10)

  def test_export_ude_no_base_with_maps_with_code(self):
    ude = Ude(
      name="ude name",
      maps=[Map(unicode=str(x), code=str(x * 2)) for x in range(10)],
    )
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
    elem = fromstring("""<ude name="name" base="base" />""")
    ude = Ude(elem, name="override name")
    self.assertEqual(ude._source_elem, elem)
    self.assertEqual(ude.name, "override name")
    self.assertEqual(ude.base, "base")

  def test_use_ude_dunder_methods(self):
    ude = Ude()
    ude.maps = "ude name"
    self.assertEqual(ude.name, ude["name"])
    ude["name"] = "new name"
    self.assertEqual(ude["name"], "new name")
    with self.assertRaises(KeyError):
      ude["unknown"]
    with self.assertRaises(KeyError):
      ude["unknown"] = "test"
    del ude["name"]
    self.assertIsNone(ude.name)
    ude.maps = [Map(unicode="unicode")]
    for i in ude:
      self.assertIsInstance(i, Map)

  def test_create_ude_from_element_wrong_tag(self):
    with self.assertRaises(ValueError):
      Ude(fromstring("<wrong_tag/>"))

  def test_export_ude_wrong_attribute_type(self):
    ude = Ude()
    ude.name = 123
    with self.assertRaises(TypeError):
      ude.to_element()

  def test_export_ude_various_iterable(self):
    ude = Ude(name="ude name")

    # tuple
    ude.maps = (Map(unicode="unicode"),)
    elem = ude.to_element()
    self.assertEqual(elem.tag, "ude")
    self.assertEqual(len(elem), 1)
    self.assertEqual(len(elem.attrib), 1)
    self.assertEqual(elem.find("map").get("unicode"), "unicode")

    # generator
    ude.maps = (Map(unicode="unicode") for x in range(1))
    elem = ude.to_element()
    self.assertEqual(elem.tag, "ude")
    self.assertEqual(len(elem), 1)
    self.assertEqual(len(elem.attrib), 1)
    self.assertEqual(elem.find("map").get("unicode"), "unicode")

    # set
    ude.maps = {Map(unicode="unicode")}
    elem = ude.to_element()
    elem = ude.to_element()
    self.assertEqual(elem.tag, "ude")
    self.assertEqual(len(elem), 1)
    self.assertEqual(len(elem.attrib), 1)
    self.assertEqual(elem.find("map").get("unicode"), "unicode")

    # dict_values
    ude.maps = {1: Map(unicode="unicode")}.values()
    elem = ude.to_element()
    elem = ude.to_element()
    self.assertEqual(elem.tag, "ude")
    self.assertEqual(len(elem), 1)
    self.assertEqual(len(elem.attrib), 1)
    self.assertEqual(elem.find("map").get("unicode"), "unicode")
