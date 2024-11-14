import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Prop


class TestCreateProp:
    correct_lxml = lxmlET.fromstring(
        """<prop xml:lang="lxml test value for lang"
        type="lxml test value for type"
        o-encoding="lxml test value for encoding">lxml test value for text</prop>"""
    )
    correct_stdlib = stdET.fromstring(
        """<prop xml:lang="stdlib test value for lang"
        type="stdlib test value for type"
        o-encoding="stdlib test value for encoding">stdlib test value for text</prop>"""
    )
    wrong_lxml = lxmlET.fromstring("""<wrongprop />""")
    wrong_stdlib = stdET.fromstring("""<wrongprop />""")
    unknown_lxml = lxmlET.fromstring(
        """<prop xml:lang="lxml test value for lang"
        type="lxml test value for type"
        o-encoding="lxml test value for encoding"
        unknown="lxml test value for unknown">lxml test value for text</prop>"""
    )
    unknown_stdlib = stdET.fromstring(
        """<prop xml:lang="stdlib test value for lang"
        type="stdlib test value for type"
        o-encoding="stdlib test value for encoding"
        unknown="stdlib test value for unknown">stdlib test value for text</prop>"""
    )

    # ==========================================================================
    #     Tests the creation of a Prop
    # ==========================================================================
    def test_create_empty_prop(self):
        """
        Test that an empty Prop can be created
        """
        prop = Prop()
        assert prop.lang is None
        assert prop.encoding is None
        assert prop.text is None
        assert prop.type is None
        assert prop._source_elem is None

    def test_create_prop_from_element(self):
        """
        Test that a Prop can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        lxmlprop = Prop(self.correct_lxml)
        assert lxmlprop.lang == "lxml test value for lang"
        assert lxmlprop.encoding == "lxml test value for encoding"
        assert lxmlprop.text == "lxml test value for text"
        assert lxmlprop.type == "lxml test value for type"
        assert lxmlprop._source_elem is self.correct_lxml
        # Check ElementTree
        stdlib_prop = Prop(self.correct_stdlib)
        assert stdlib_prop.lang == "stdlib test value for lang"
        assert stdlib_prop.encoding == "stdlib test value for encoding"
        assert stdlib_prop.text == "stdlib test value for text"
        assert stdlib_prop.type == "stdlib test value for type"
        assert stdlib_prop._source_elem is self.correct_stdlib

    def test_create_prop_from_wrong_element_tag(self):
        """
        Test that a Prop cannot be created from an element with a wrong tag
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Prop(self.wrong_lxml)
        # Check ElementTree
        with pytest.raises(ValueError):
            Prop(self.wrong_stdlib)

    def test_create_prop_from_element_override_values(self):
        """
        Test that a Prop can be created from an xml element with keyword
        arguments and that the keyword arguments override the values in the
        element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_prop = Prop(
            self.correct_lxml,
            text="lxml override test value for text",
            lang="lxml override test value for lang",
            encoding="lxml override test value for encoding",
            type="lxml override test value for type",
        )
        assert lxml_prop.text == "lxml override test value for text"
        assert lxml_prop.lang == "lxml override test value for lang"
        assert lxml_prop.encoding == "lxml override test value for encoding"
        assert lxml_prop.type == "lxml override test value for type"
        assert lxml_prop._source_elem is self.correct_lxml
        # Check ElementTree
        stdlib_prop = Prop(
            self.correct_stdlib,
            text="stdlib override test value for text",
            lang="stdlib override test value for lang",
            encoding="stdlib override test value for encoding",
            type="stdlib override test value for type",
        )
        assert stdlib_prop.text == "stdlib override test value for text"
        assert stdlib_prop.lang == "stdlib override test value for lang"
        assert stdlib_prop.encoding == "stdlib override test value for encoding"
        assert stdlib_prop.type == "stdlib override test value for type"
        assert stdlib_prop._source_elem is self.correct_stdlib

    def test_create_prop_from_element_with_unknown_attribute(self):
        """
        Test that a Note can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Note's __dir__()
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_prop = Prop(self.unknown_lxml)
        assert lxml_prop.lang == "lxml test value for lang"
        assert lxml_prop.encoding == "lxml test value for encoding"
        assert lxml_prop.text == "lxml test value for text"
        assert lxml_prop.type == "lxml test value for type"
        assert lxml_prop._source_elem is self.unknown_lxml
        assert "unknown" not in lxml_prop.__dir__()

        # Check ElementTree
        stdlib_prop = Prop(self.unknown_stdlib)
        assert stdlib_prop.lang == "stdlib test value for lang"
        assert stdlib_prop.encoding == "stdlib test value for encoding"
        assert stdlib_prop.text == "stdlib test value for text"
        assert stdlib_prop.type == "stdlib test value for type"
        assert stdlib_prop._source_elem is self.unknown_stdlib
        assert "unknown" not in stdlib_prop.__dir__()

    def test_create_prop_with_non_string_attribute_value(self):
        """
        Test that a Prop can be created with a non-string attribute value
        """
        note = Prop(lang=1, encoding=2, text=3, type=4)
        assert note.lang == 1
        assert note.encoding == 2
        assert note.text == 3
        assert note.type == 4

    # ==========================================================================
    #     Tests the export of a Prop
    # ==========================================================================
    def test_export_empty_prop(self):
        """
        Test that an empty Note cannot be exported
        """
        with pytest.raises(AttributeError):
            Prop().to_element()

    def test_export_prop_with_all_attributes(self):
        """
        Test that a Prop can be exported with all its attributes
        """
        prop = Prop(
            lang="test value for lang",
            encoding="test value for encoding",
            text="test value for text",
            type="test value for type",
        )
        elem = prop.to_element()
        assert elem.tag == "prop"
        assert len(elem) == 0
        assert (
            elem.get("{http://www.w3.org/XML/1998/namespace}lang")
            == "test value for lang"
        )
        assert elem.get("o-encoding") == "test value for encoding"
        assert elem.text == "test value for text"
        assert elem.get("type") == "test value for type"

    def test_export_prop_from_element(self):
        """
        Test that a Prop can be created from an xml element and is the same
        as the original
        Test both lxml and stdlib
        """
        # Check lxml
        prop = Prop(self.correct_lxml)
        new_lxml_elem = prop.to_element()
        assert new_lxml_elem.tag == new_lxml_elem.tag
        assert len(self.correct_lxml) == len(new_lxml_elem)
        assert new_lxml_elem.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        ) == self.correct_lxml.get("{http://www.w3.org/XML/1998/namespace}lang")
        assert new_lxml_elem.get("o-encoding") == self.correct_lxml.get("o-encoding")
        assert new_lxml_elem.text == self.correct_lxml.text
        assert new_lxml_elem.get("type") == self.correct_lxml.get("type")
        # Check ElementTree
        prop = Prop(self.correct_stdlib)
        new_stdlib_elem = prop.to_element()
        assert new_stdlib_elem.tag == self.correct_stdlib.tag
        assert len(self.correct_stdlib) == len(new_stdlib_elem)
        assert new_stdlib_elem.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        ) == self.correct_stdlib.get("{http://www.w3.org/XML/1998/namespace}lang")
        assert new_stdlib_elem.get("o-encoding") == self.correct_stdlib.get(
            "o-encoding"
        )
        assert new_stdlib_elem.text == self.correct_stdlib.text
        assert new_stdlib_elem.get("type") == self.correct_stdlib.get("type")

    def test_export_prop_missing_required_attributes(self):
        """
        Test that a Prop cannot be exported if it is missing required attributes
        """
        prop = Prop(
            lang="test value for lang",
            encoding="test value for encoding",
            type="test value for type",
        )
        with pytest.raises(AttributeError):
            prop.to_element()

    def test_export_prop_with_non_string_attributes(self):
        """
        Test that a Prop cannot be exported with non-string attributes
        """
        prop = Prop(
            text=1,
            lang=2,
            encoding=3,
            type=4,
        )
        with pytest.raises(TypeError):
            prop.to_element()
