import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Ude


class TestUde:
    # ==========================================================================
    #     Tests the creation of a Ude
    # ==========================================================================
    def test_create_empty_ude(self):
        """
        Test that an empty Ude can be created
        """
        ude = Ude()
        assert ude.base is None
        assert ude.name is None
        assert ude.maps == []

    def test_create_ude_from_lxml_element(self):
        """
        Test that a Ude can be created from an lxml element
        """
        elem = lxmlET.fromstring(
            """<ude name="test value for name" base="test value for base">
            <map unicode="test value for unicode 1" code="test value for code 1"
            ent="test value for ent 1" subst="test value for subst 1" />
            <map unicode="test value for unicode 2" code="test value for code 2"
            ent="test value for ent 2" subst="test value for subst 2" />
            </ude>"""
        )
        ude = Ude(elem)
        assert ude.name == "test value for name"
        assert ude.base == "test value for base"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "test value for unicode 1"
        assert ude.maps[0].code == "test value for code 1"
        assert ude.maps[0].ent == "test value for ent 1"
        assert ude.maps[0].subst == "test value for subst 1"
        assert ude.maps[1].unicode == "test value for unicode 2"
        assert ude.maps[1].code == "test value for code 2"
        assert ude.maps[1].ent == "test value for ent 2"
        assert ude.maps[1].subst == "test value for subst 2"

    def test_create_ude_from_wrong_element_tag(self):
        """
        Test that a Ude cannot be created from an element with a wrong tag
        """
        elem = lxmlET.fromstring(
            """<wrongude name="test value for name" base="test value for base">
            <map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />
            </wrongude>"""
        )
        with pytest.raises(ValueError):
            Ude(elem)

    def test_create_ude_from_stdlib_element(self):
        """
        Test that a Ude can be created from a stdlib Element
        """
        elem = stdET.fromstring(
            """<ude name="test value for name" base="test value for base">
            <map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />
            </ude>"""
        )
        ude = Ude(elem)
        assert ude.name == "test value for name"
        assert ude.base == "test value for base"
        assert len(ude.maps) == 1
        assert ude.maps[0].unicode == "test value for unicode"
        assert ude.maps[0].code == "test value for code"
        assert ude.maps[0].ent == "test value for ent"
        assert ude.maps[0].subst == "test value for subst"

    def test_create_ude_from_lxml_element_with_keyword_arguments(self):
        """
        Test that a Ude can be created from an lxml element with keyword
        arguments
        """
        elem = lxmlET.fromstring(
            """<ude name="test value for name" base="test value for base">
            <map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />
            </ude>"""
        )
        ude = Ude(
            elem,
            name="override value for name",
            base="override value for base",
        )
        assert ude.name == "override value for name"
        assert ude.base == "override value for base"
        assert len(ude.maps) == 1
        assert ude.maps[0].unicode == "test value for unicode"
        assert ude.maps[0].code == "test value for code"
        assert ude.maps[0].ent == "test value for ent"
        assert ude.maps[0].subst == "test value for subst"

    def test_create_ude_from_stdlib_element_with_keyword_arguments(self):
        """
        Test that a Ude can be created from a stdlib Element with keyword
        arguments
        """
        elem = stdET.fromstring(
            """<ude name="test value for name" base="test value for base">
            <map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst" />
            </ude>"""
        )
        ude = Ude(
            elem,
            name="override value for name",
            base="override value for base",
        )
        assert ude.name == "override value for name"
        assert ude.base == "override value for base"
        assert len(ude.maps) == 1
        assert ude.maps[0].unicode == "test value for unicode"
        assert ude.maps[0].code == "test value for code"
        assert ude.maps[0].ent == "test value for ent"
        assert ude.maps[0].subst == "test value for subst"

    def test_create_ude_from_lxml_element_with_unknown_attribute(self):
        """
        Test that a Ude can be created from an lxml element with an unknown
        attribute and that the ubnknown attribute is not in the Ude's __dir__()
        """
        elem = lxmlET.fromstring(
            """<ude name="test value for name" base="test value for base">
            <map unicode="test value for unicode" code="test value for code"
            ent="test value for ent" subst="test value for subst"
            unknown="test value for unknown" />
            </ude>"""
        )
        ude = Ude(elem)
        assert ude.name == "test value for name"
        assert ude.base == "test value for base"
        assert len(ude.maps) == 1
        assert ude.maps[0].unicode == "test value for unicode"
        assert ude.maps[0].code == "test value for code"
        assert ude.maps[0].ent == "test value for ent"
        assert ude.maps[0].subst == "test value for subst"
        assert "unknown" not in ude.__dir__()

    def test_add_unknown_attribute_to_ude(self):
        """
        Test that a Ude won't accept an unknown attribute
        """
        ude = Ude()
        with pytest.raises(AttributeError):
            ude.unknown = "test value for unknown"

    def test_non_string_attribute_value_to_ude(self):
        """
        Test that any Ude attribute can be set to any non-string value
        """
        ude = Ude()
        ude.name = 1
        ude.base = (1, 2)
        ude.maps = [1, 2]
        assert ude.name == 1
        assert ude.base == (1, 2)
        assert ude.maps == [1, 2]
