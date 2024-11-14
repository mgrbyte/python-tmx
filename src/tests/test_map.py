import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Map


class TestMap:
    correct_lxml = lxmlET.fromstring(
        """<map unicode="lxml test value for unicode" code="lxml test value for code"
        ent="lxml test value for ent" subst="lxml test value for subst" />"""
    )
    correct_stdlib = stdET.fromstring(
        """<map unicode="stdlib test value for unicode" code="stdlib test value for code"
        ent="stdlib test value for ent" subst="stdlib test value for subst" />"""
    )
    wrong_lxml = lxmlET.fromstring("""<wrongmap />""")
    wrong_stdlib = stdET.fromstring("""<wrongmap />""")
    unknown_lxml = lxmlET.fromstring(
        """<map unicode="test value for unicode" code="test value for code"
        ent="test value for ent" subst="test value for subst"
        unknown="test value for unknown" />"""
    )
    unknown_stdlib = stdET.fromstring(
        """<map unicode="test value for unicode" code="test value for code"
        ent="test value for ent" subst="test value for subst"
        unknown="test value for unknown" />"""
    )

    # ==========================================================================
    #     Tests the creation of a Map
    # ==========================================================================
    def test_create_empty_map(self):
        """
        Test that an empty Map can be created
        """
        empty_map = Map()
        assert empty_map.unicode is None
        assert empty_map.code is None
        assert empty_map.ent is None
        assert empty_map.subst is None
        assert empty_map._source_elem is None

    def test_create_map_from_element(self):
        """
        Test that a Map can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_map = Map(self.correct_lxml)
        assert lxml_map.unicode == "lxml test value for unicode"
        assert lxml_map.code == "lxml test value for code"
        assert lxml_map.ent == "lxml test value for ent"
        assert lxml_map.subst == "lxml test value for subst"
        assert lxml_map._source_elem is self.correct_lxml
        # Check ElementTree
        stdlb_map = Map(self.correct_stdlib)
        assert stdlb_map.unicode == "stdlib test value for unicode"
        assert stdlb_map.code == "stdlib test value for code"
        assert stdlb_map.ent == "stdlib test value for ent"
        assert stdlb_map.subst == "stdlib test value for subst"
        assert stdlb_map._source_elem is self.correct_stdlib

    def test_create_map_from_wrong_element_tag(self):
        """
        Test that a Map cannot be created from an element with a wrong tag
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Map(self.wrong_lxml)

        # Check ElementTree
        with pytest.raises(ValueError):
            Map(self.wrong_stdlib)

    def test_create_map_from_element_override_values(self):
        """
        Test that a Map can be created from an xml element with keyword
        arguments and that the keyword arguments override the values in the
        element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_map = Map(
            self.correct_lxml,
            unicode="override value for unicode",
            code="override value for code",
        )
        assert lxml_map.unicode == "override value for unicode"
        assert lxml_map.code == "override value for code"
        assert lxml_map.ent == "lxml test value for ent"
        assert lxml_map.subst == "lxml test value for subst"
        # Check ElementTree
        stdlib_map = Map(
            self.correct_stdlib,
            unicode="override value for unicode",
            code="override value for code",
        )
        assert stdlib_map.unicode == "override value for unicode"
        assert stdlib_map.code == "override value for code"
        assert stdlib_map.ent == "stdlib test value for ent"
        assert stdlib_map.subst == "stdlib test value for subst"

    def test_create_map_from_element_with_unknown_attribute(self):
        """
        Test that a Map can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Map's __dir__()
        Test both lxml and stdlib
        """
        # Check lxml
        map = Map(self.unknown_lxml)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert "unknown" not in map.__dir__()
        # Check ElementTree
        map = Map(self.unknown_stdlib)
        assert map.unicode == "test value for unicode"
        assert map.code == "test value for code"
        assert map.ent == "test value for ent"
        assert map.subst == "test value for subst"
        assert "unknown" not in map.__dir__()

    def test_create_or_add_map_with_unknown_attribute(self):
        """
        Test that a Map cannot be created if passing an unknown attribute
        """
        with pytest.raises(TypeError):
            Map(
                name="lxml test value for name",
                base="lxml test value for base",
                unknown="should not appear",
            )
        map = Map()
        with pytest.raises(AttributeError):
            map.unknown = "test value for unknown"

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
        Test both lxml and stdlib
        """
        # Check lxml
        map = Map(self.correct_lxml)
        new_lxml_elem = map.to_element()
        assert new_lxml_elem.tag == new_lxml_elem.tag
        assert len(new_lxml_elem) == len(self.correct_lxml)
        assert new_lxml_elem.get("unicode") == self.correct_lxml.get("unicode")
        assert new_lxml_elem.get("code") == self.correct_lxml.get("code")
        assert new_lxml_elem.get("ent") == self.correct_lxml.get("ent")
        assert new_lxml_elem.get("subst") == self.correct_lxml.get("subst")
        # Check ElementTree
        map = Map(self.correct_stdlib)
        new_stdlib_elem = map.to_element()
        assert new_stdlib_elem.tag == self.correct_stdlib.tag
        assert len(new_lxml_elem) == len(self.correct_stdlib)
        assert new_stdlib_elem.get("unicode") == self.correct_stdlib.get("unicode")
        assert new_stdlib_elem.get("code") == self.correct_stdlib.get("code")
        assert new_stdlib_elem.get("ent") == self.correct_stdlib.get("ent")
        assert new_stdlib_elem.get("subst") == self.correct_stdlib.get("subst")

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
