import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Map


class TestMap:
    # ==========================================================================
    #     Tests the creation of a Map
    # ==========================================================================
    def test_can_create_empty_map(self):
        """
        Test that an empty Map can be created
        """
        map = Map()
        assert map.unicode is None
        assert map.code is None
        assert map.ent is None
        assert map.subst is None
        assert map._source_elem is None

    def test_can_create_map_from_element(self):
        """
        Test that a Map can be created from an xml element
        """
        # Check lxml
        elem = lxmlET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(elem)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert map._source_elem is elem
        # Check ElementTree
        elem = stdET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(elem)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert map._source_elem is elem

    def test_create_map_from_wrong_element_tag(self):
        """
        Test that a Map cannot be created from an element with a wrong tag
        """
        elem = lxmlET.fromstring(
            """<wrongmap unicode="test value for unicode"
            code="test value for code" ent="test value for ent"
            subst="test value for subst" />"""
        )
        with pytest.raises(ValueError):
            Map(elem)

    def test_create_map_from_element_override_values(self):
        """
        Test that a Map can be created from an xml element with keyword
        arguments and that the keyword arguments override the values in the
        element
        """
        # Check lxml
        elem = lxmlET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(
            elem,
            unicode="override value for unicode",
            code="override value for code",
        )
        assert map.unicode == "override value for unicode"
        assert map.code == "override value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        # Check ElementTree
        elem = stdET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(
            elem,
            unicode="override value for unicode",
            code="override value for code",
        )
        assert map.unicode == "override value for unicode"
        assert map.code == "override value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"

    def test_create_map_from_element_with_unknown_attribute(self):
        """
        Test that a Map can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Map's __dir__()
        """
        # Check lxml
        elem = lxmlET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst"
            unknown="test value for unknown" />"""
        )
        map = Map(elem)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert "unknown" not in map.__dir__()
        # Check ElementTree
        elem = stdET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst"
            unknown="test value for unknown" />"""
        )
        map = Map(elem)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert "unknown" not in map.__dir__()

    def test_create_map_with_non_string_attribute_value(self):
        """
        Test that a Map can be created with a non-string attribute value
        """
        map = Map(unicode=1)
        assert map.unicode == 1

    # ==========================================================================
    #     Tests the export of a Map
    # ==========================================================================
    def test_export_empty_map(self):
        """
        Test that an empty Map cannot be exported
        """
        map = Map()
        with pytest.raises(AttributeError):
            map.to_element()

    def test_export_map_with_all_attributes(self):
        """
        Test that a Map can be exported with all its attributes
        """
        map = Map(
            unicode="test value for unicode",
            code="test value for code",
            ent="test value for ent",
            subst="test value for subst",
        )
        elem = map.to_element()
        assert elem.tag == "map"
        assert len(elem) == 0
        assert elem.get("unicode") == "test value for unicode"
        assert elem.get("code") == "test value for code"
        assert elem.get("ent") == "test value for ent"
        assert elem.get("subst") == "test value for subst"

    def test_export_map_from_element(self):
        """
        Test that a Map can be created from an xml element and is the same
        as the original
        """
        # Check lxml
        elem = lxmlET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(elem)
        new_elem = map.to_element()
        assert new_elem.tag == elem.tag
        assert len(elem) == len(new_elem)
        assert elem.get("unicode") == new_elem.get("unicode")
        assert elem.get("code") == new_elem.get("code")
        assert elem.get("ent") == new_elem.get("ent")
        assert elem.get("subst") == new_elem.get("subst")
        # Check ElementTree
        elem = stdET.fromstring(
            """<map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />"""
        )
        map = Map(elem)
        new_elem = map.to_element()
        assert new_elem.tag == elem.tag
        assert len(elem) == len(new_elem)
        assert elem.get("unicode") == new_elem.get("unicode")
        assert elem.get("code") == new_elem.get("code")
        assert elem.get("ent") == new_elem.get("ent")
        assert elem.get("subst") == new_elem.get("subst")

    def test_export_map_missing_required_attributes(self):
        """
        Test that a Map cannot be exported if it is missing required attributes
        """
        map = Map(
            code="test value for code",
            ent="test value for ent",
            subst="test value for subst",
        )
        with pytest.raises(AttributeError):
            map.to_element()

    def test_export_map_with_non_string_attributes(self):
        """
        Test that a Map cannot be exported with non-string attributes
        """
        map = Map(
            unicode=1,
            code=2,
            ent=3,
            subst=4,
        )
        with pytest.raises(TypeError):
            map.to_element()

    # ==========================================================================
    #     Tests the attributes of a Map
    # ==========================================================================
    def test_add_unknown_attribute_to_map(self):
        """
        Test that a Map won't accept an unknown attribute
        """
        map = Map()
        with pytest.raises(AttributeError):
            map.unknown = "test value for unknown"

    def test_non_string_attribute_value_to_map(self):
        """
        Test that any Map attribute can be set to non-string value
        """
        map = Map()
        map.unicode = 1
        map.code = (1, 2)
        map.ent = [1, 2]
        map.subst = {1, 2}
        assert map.unicode == 1
        assert map.code == (1, 2)
        assert map.ent == [1, 2]
        assert map.subst == {1, 2}
