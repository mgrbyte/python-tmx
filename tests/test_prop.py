from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Prop


class TestProp(TestCase):
  def test_create_export_empty_prop(self):
    prop = Prop()
    for attr in prop.__slots__:
      self.assertIsNone(getattr(prop, attr))
    with self.assertRaises(AttributeError):
      prop.to_element()

  def test_create_prop_from_element(self):
    elem = fromstring(
      """<prop xml:lang="en-US" o-encoding="utf-8" type="x-test">prop text</prop>"""
    )
    prop = Prop(elem)
    self.assertEqual(prop._source_elem, elem)
    self.assertEqual(prop.text, elem.text)
    self.assertEqual(prop.lang, elem.get("{http://www.w3.org/XML/1998/namespace}lang"))
    self.assertEqual(prop.encoding, elem.get("o-encoding"))
    self.assertEqual(prop.type, elem.get("type"))

  def test_export_minimal_prop(self):
    prop = Prop(text="prop text", type="x-test")
    elem = prop.to_element()
    self.assertEqual(elem.text, prop.text)
    self.assertEqual(elem.tag, "prop")
    self.assertEqual(len(elem), 0)
    self.assertEqual(len(elem.attrib), 1)

  def test_add_unknown_attributes(self):
    prop = Prop()
    with self.assertRaises(AttributeError):
      prop.other = "test"

  def test_create_prop_from_element_with_unknwon_attributes(self):
    elem = fromstring("""<prop other="other"/>""")
    new_prop = Prop(elem)
    self.assertNotIn("other", new_prop.__dir__())

  def test_create_prop_from_element_with_kwargs(self):
    prop = Prop(
      fromstring("""<prop xml:lang="en-US" o-encoding="utf-8">prop text</prop>"""),
      text="override text",
    )
    self.assertEqual(prop.text, "override text")
    self.assertEqual(prop.lang, "en-US")
    self.assertEqual(prop.encoding, "utf-8")

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
    del prop["text"]
    self.assertIsNone(prop.text)

  def test_create_prop_from_element_wrong_tag(self):
    with self.assertRaises(ValueError):
      Prop(fromstring("<wrong_tag/>"))

  def test_export_prop_wrong_attribute_type(self):
    prop = Prop()
    prop.text = 123
    prop.type = 456
    with self.assertRaises(TypeError):
      prop.to_element()

  def test_export_full_prop(self):
    prop = Prop(
      text="prop text",
      lang="en-US",
      encoding="utf-8",
      type="x-test",
    )
    elem = prop.to_element()
    self.assertEqual(elem.text, prop.text)
    self.assertEqual(elem.tag, "prop")
    self.assertEqual(len(elem), 0)
    self.assertEqual(len(elem.attrib), 3)
    self.assertEqual(elem.get("{http://www.w3.org/XML/1998/namespace}lang"), "en-US")
    self.assertEqual(elem.get("o-encoding"), "utf-8")
    self.assertEqual(elem.get("type"), "x-test")
