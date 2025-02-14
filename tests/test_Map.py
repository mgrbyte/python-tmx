import xml.etree.ElementTree as pyet

import lxml.etree as lxet
import pytest

from PythonTmx.classes import ENGINE, Map


@pytest.fixture
def correct_elem_python() -> pyet.Element:
  return pyet.Element(
    "map",
    attrib={
      "unicode": "#xF8FF",
      "code": "#xF0",
      "ent": "Apple_logo",
      "subst": "[Apple]",
    },
  )


@pytest.fixture
def correct_elem_lxml() -> lxet._Element:
  return lxet.Element(
    "map",
    attrib={
      "unicode": "#xF8FF",
      "code": "#xF0",
      "ent": "Apple_logo",
      "subst": "[Apple]",
    },
  )


class TestMap:
  def test_init(self) -> None:
    map = Map(unicode="F8FF", code="F0", ent="Apple_logo", subst="[Apple]")
    assert map.unicode == "F8FF"
    assert map.code == "F0"
    assert map.ent == "Apple_logo"
    assert map.subst == "[Apple]"

  def test_empy_init(self) -> None:
    with pytest.raises(TypeError):
      Map()

  def test_minimum_init(self) -> None:
    map = Map(
      unicode="#xF8FF",
    )
    assert map.unicode == "#xF8FF"
    assert map.code is None
    assert map.ent is None
    assert map.subst is None

  def test_from_element_python(self, correct_elem_python: pyet.Element) -> None:
    map = Map.from_element(correct_elem_python)
    assert map.unicode == "#xF8FF" == correct_elem_python.attrib["unicode"]
    assert map.code == "#xF0" == correct_elem_python.attrib["code"]
    assert map.ent == "Apple_logo" == correct_elem_python.attrib["ent"]
    assert map.subst == "[Apple]" == correct_elem_python.attrib["subst"]

  def test_from_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    map = Map.from_element(correct_elem_python, ent="new ent", subst="new subst")
    assert map.unicode == "#xF8FF" == correct_elem_python.attrib["unicode"]
    assert map.code == "#xF0" == correct_elem_python.attrib["code"]
    assert map.ent == "new ent" != correct_elem_python.attrib["ent"]
    assert map.subst == "new subst" != correct_elem_python.attrib["subst"]

  def test_from_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    map = Map.from_element(correct_elem_lxml)
    assert map.unicode == "#xF8FF" == correct_elem_lxml.attrib["unicode"]
    assert map.code == "#xF0" == correct_elem_lxml.attrib["code"]
    assert map.ent == "Apple_logo" == correct_elem_lxml.attrib["ent"]
    assert map.subst == "[Apple]" == correct_elem_lxml.attrib["subst"]

  def test_from_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    map = Map.from_element(correct_elem_lxml, ent="new ent", subst="new subst")
    assert map.unicode == "#xF8FF" == correct_elem_lxml.attrib["unicode"]
    assert map.code == "#xF0" == correct_elem_lxml.attrib["code"]
    assert map.ent == "new ent" != correct_elem_lxml.attrib["ent"]
    assert map.subst == "new subst" != correct_elem_lxml.attrib["subst"]

  def test_to_element_python(self, correct_elem_python: pyet.Element) -> None:
    map = Map.from_element(correct_elem_python)
    map_elem = map.to_element(ENGINE.PYTHON)
    assert map_elem.tag == correct_elem_python.tag == "map"
    assert dict(map_elem.attrib) == correct_elem_python.attrib

  def test_to_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    map = Map.from_element(correct_elem_python)
    map_elem = map.to_element(ENGINE.PYTHON, ent="new ent", subst="new subst")
    assert map_elem.tag == correct_elem_python.tag == "map"
    assert dict(map_elem.attrib) != dict(correct_elem_python.attrib)
    assert map_elem.attrib["ent"] == "new ent"
    assert map_elem.attrib["subst"] == "new subst"

  def test_to_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    map = Map.from_element(correct_elem_lxml)
    map_elem = map.to_element(ENGINE.LXML)
    assert map_elem.tag == correct_elem_lxml.tag == "map"
    assert dict(map_elem.attrib) == dict(correct_elem_lxml.attrib)

  def test_to_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    map = Map.from_element(correct_elem_lxml)
    map_elem = map.to_element(ENGINE.LXML, ent="new ent", subst="new subst")
    assert map_elem.tag == correct_elem_lxml.tag == "map"
    assert dict(map_elem.attrib) != dict(correct_elem_lxml.attrib)
    assert map_elem.attrib["ent"] == "new ent"
    assert map_elem.attrib["subst"] == "new subst"

  def test_from_element_invalid(self) -> None:
    with pytest.raises(ValueError):
      Map.from_element(pyet.Element("test"))

  def test_incorrect_attrib_type_export(self) -> None:
    map = Map(unicode="#xf8ff", subst=123)
    with pytest.raises(TypeError):
      map.to_element()

  def test_incorrect_unicode_export(self) -> None:
    map = Map(unicode="123")
    with pytest.raises(ValueError):
      map.to_element()
    map.unicode = "#xzzzz"
    with pytest.raises(ValueError):
      map.to_element()
    map.unicode = "#x10ffffffff"
    with pytest.raises(ValueError):
      map.to_element()

  def test_incorrect_code_export(self) -> None:
    map = Map(unicode="#xF8FF", code="123")
    with pytest.raises(ValueError):
      map.to_element()
    map.code = "#xzzzz"
    with pytest.raises(ValueError):
      map.to_element()
    map.code = "#x10ffffffff"
    with pytest.raises(ValueError):
      map.to_element()

  def test_extra_attrib(self) -> None:
    with pytest.raises(TypeError):
      Map(
        unicode="#xF8FF", code="#xF0", extra="test", ent="Apple_logo", subst="[Apple]"
      )

  def test_extra_attrib_from_element_python(
    self, correct_elem_python: pyet.Element
  ) -> None:
    elem = correct_elem_python
    elem.set("extra", "test")
    map = Map.from_element(elem)
    assert hasattr(map, "extra") is False

  def test_extra_attrib_from_element_lxml(
    self, correct_elem_lxml: lxet._Element
  ) -> None:
    elem = correct_elem_lxml
    elem.set("extra", "test")
    map = Map.from_element(elem)
    assert hasattr(map, "extra") is False

  def test_wrong_engine(self) -> None:
    with pytest.raises(ValueError):
      Map(unicode="#xF8FF", code="#xF0").to_element("wrong")

  def test_engines(self) -> None:
    map = Map(unicode="#xF8FF", code="#xF0")
    assert isinstance(map.to_element(ENGINE.LXML), lxet._Element)
    assert isinstance(map.to_element(ENGINE.PYTHON), pyet.Element)

  def test_add_extra(self) -> None:
    map = Map(unicode="#xF8FF", code="#xF0")
    map_elem = map.to_element(ENGINE.PYTHON, add_extra=True, extra="test")
    assert map_elem.tag == "map"
    assert map_elem.attrib["extra"] == "test"
