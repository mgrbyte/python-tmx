import xml.etree.ElementTree as pyet

import lxml.etree as lxet
import pytest

from PythonTmx.classes import ENGINE, Map, Ude


@pytest.fixture
def correct_elem_python() -> pyet.Element:
  elem = pyet.Element(
    "ude",
    attrib={
      "name": "test",
      "base": "test",
    },
  )
  elem.extend(
    [
      pyet.Element(
        "map",
        attrib={
          "unicode": "#xF8FF",
          "code": "#xF0",
          "ent": "Apple_logo",
          "subst": "[Apple]",
        },
      )
      for _ in range(3)
    ]
  )
  return elem


@pytest.fixture
def correct_elem_lxml() -> lxet._Element:
  elem = lxet.Element(
    "ude",
    attrib={
      "name": "test",
      "base": "test",
    },
  )
  elem.extend(
    [
      lxet.Element(
        "map",
        attrib={
          "unicode": "#xF8FF",
          "code": "#xF0",
          "ent": "Apple_logo",
          "subst": "[Apple]",
        },
      )
      for _ in range(3)
    ]
  )
  return elem


class TestUde:
  def test_init(self) -> None:
    ude = Ude(name="test", base="test", maps=[Map(unicode="#xF8FF")])
    assert ude.name == "test"
    assert ude.base == "test"
    assert len(ude.maps) == 1
    assert ude.maps[0] == Map(unicode="#xF8FF")

  def test_empy_init(self) -> None:
    with pytest.raises(TypeError):
      Ude()

  def test_minimum_init(self) -> None:
    ude = Ude(name="test")
    assert ude.name == "test"
    assert ude.base is None
    assert ude.maps == []

  def test_from_element_python(self, correct_elem_python: pyet.Element) -> None:
    ude = Ude.from_element(correct_elem_python)
    assert ude.name == "test" == correct_elem_python.attrib["name"]
    assert ude.base == "test" == correct_elem_python.attrib["base"]
    assert len(ude.maps) == 3
    assert ude.maps == [
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
    ]

  def test_from_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    ude = Ude.from_element(
      correct_elem_python,
      name="new name",
      base="new base",
      maps=[
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      ],
    )
    assert ude.name == "new name" != correct_elem_python.attrib["name"]
    assert ude.base == "new base" != correct_elem_python.attrib["base"]
    assert len(ude.maps) == 3
    assert ude.maps == [
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
    ]

  def test_from_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    ude = Ude.from_element(correct_elem_lxml)
    assert ude.name == "test" == correct_elem_lxml.attrib["name"]
    assert ude.base == "test" == correct_elem_lxml.attrib["base"]
    assert len(ude.maps) == 3
    assert ude.maps == [
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="Apple_logo", subst="[Apple]"),
    ]

  def test_from_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    ude = Ude.from_element(
      correct_elem_lxml,
      name="new name",
      base="new base",
      maps=[
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
        Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      ],
    )
    assert ude.name == "new name" != correct_elem_lxml.attrib["name"]
    assert ude.base == "new base" != correct_elem_lxml.attrib["base"]
    assert len(ude.maps) == 3
    assert ude.maps == [
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
      Map(unicode="#xF8FF", code="#xF0", ent="New", subst="[Apple]"),
    ]

  def test_to_element_python(self, correct_elem_python: pyet.Element) -> None:
    ude = Ude.from_element(correct_elem_python)
    elem = ude.to_element()
    assert elem.tag == correct_elem_python.tag == "ude"
    assert elem.attrib == correct_elem_python.attrib
    for i in range(len(elem)):
      assert elem[i].tag == correct_elem_python[i].tag == "map"
      assert elem[i].attrib == correct_elem_python[i].attrib

  def test_to_element_python_kwargs(self, correct_elem_python: pyet.Element) -> None:
    ude = Ude.from_element(correct_elem_python)
    elem = ude.to_element(base="new base", maps=[Map(unicode="#xF8FF", ent="new ent")])
    assert elem.tag == correct_elem_python.tag == "ude"
    assert elem.attrib["base"] == "new base" != correct_elem_python.attrib["base"]
    assert elem.attrib["name"] == "test" == correct_elem_python.attrib["name"]
    assert len(elem) == 1 != len(correct_elem_python)
    assert elem[0].tag == correct_elem_python[0].tag == "map"
    assert (
      elem[0].attrib["unicode"] == "#xF8FF" == correct_elem_python[0].attrib["unicode"]
    )
    assert elem[0].attrib["ent"] == "new ent" != correct_elem_python[0].attrib["ent"]

  def test_to_element_lxml(self, correct_elem_lxml: lxet._Element) -> None:
    ude = Ude.from_element(correct_elem_lxml)
    elem = ude.to_element()
    assert elem.tag == correct_elem_lxml.tag == "ude"
    assert elem.attrib == correct_elem_lxml.attrib
    for i in range(len(elem)):
      assert elem[i].tag == correct_elem_lxml[i].tag == "map"
      assert elem[i].attrib == correct_elem_lxml[i].attrib

  def test_to_element_lxml_kwargs(self, correct_elem_lxml: lxet._Element) -> None:
    ude = Ude.from_element(correct_elem_lxml)
    elem = ude.to_element(base="new base", maps=[Map(unicode="#xF8FF", ent="new ent")])
    assert elem.tag == correct_elem_lxml.tag == "ude"
    assert elem.attrib["base"] == "new base" != correct_elem_lxml.attrib["base"]
    assert len(elem) == 1 != len(correct_elem_lxml)
    assert elem[0].tag == correct_elem_lxml[0].tag == "map"
    assert (
      elem[0].attrib["unicode"] == "#xF8FF" == correct_elem_lxml[0].attrib["unicode"]
    )
    assert elem[0].attrib["ent"] == "new ent" != correct_elem_lxml[0].attrib["ent"]

  def test_from_element_invalid(self) -> None:
    elem = lxet.Element("wrong")
    with pytest.raises(ValueError):
      Ude.from_element(elem)

  def test_incorrect_attrib_type(self) -> None:
    ude = Ude(name=123)
    with pytest.raises(TypeError):
      ude.to_element()

  def test_export_no_base(self) -> None:
    ude = Ude(name="test", maps=[Map(unicode="#xF8FF", code="#xF0")])
    with pytest.raises(ValueError):
      ude.to_element()

  def test_export_no_code_no_base(self) -> None:
    ude = Ude(name="test", maps=[Map(unicode="#xF8FF", ent="test")])
    ude.to_element()

  def test_extra_attrib(self) -> None:
    with pytest.raises(TypeError):
      Ude(
        name="test",
        extra="test",
      )

  def test_extra_attrib_from_element_python(
    self, correct_elem_python: pyet.Element
  ) -> None:
    elem = correct_elem_python
    elem.set("extra", "test")
    ude = Ude.from_element(elem)
    assert hasattr(ude, "extra") is False

  def test_extra_attrib_from_element_lxml(
    self, correct_elem_lxml: lxet._Element
  ) -> None:
    elem = correct_elem_lxml
    elem.set("extra", "test")
    ude = Ude.from_element(elem)
    assert hasattr(ude, "extra") is False

  def test_wrong_engine(self) -> None:
    with pytest.raises(ValueError):
      Ude(name="hello").to_element("wrong")

  def test_engines(self) -> None:
    ude = Ude(name="hello")
    assert isinstance(ude.to_element(ENGINE.LXML), lxet._Element)
    assert isinstance(ude.to_element(ENGINE.PYTHON), pyet.Element)

  def test_add_extra(self) -> None:
    ude = Ude(name="hello")
    ude_elem = ude.to_element(ENGINE.PYTHON, add_extra=True, extra="test")
    assert ude_elem.tag == "ude"
    assert ude_elem.attrib["extra"] == "test"

  def test_wrong_map(self) -> None:
    ude = Ude(name="hello", maps=[13])
    with pytest.raises(TypeError):
      ude.to_element()
