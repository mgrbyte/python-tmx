import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Note


class TestCreateNote:
    correct_lxml = lxmlET.fromstring(
        """<note xml:lang="lxml test value for lang"
        o-encoding="lxml test value for encoding">lxml test value for text</note>"""
    )
    correct_stdlib = stdET.fromstring(
        """<note xml:lang="stdlib test value for lang"
        o-encoding="stdlib test value for encoding">stdlib test value for text</note>"""
    )
    wrong_lxml = lxmlET.fromstring("""<wrongnote />""")
    wrong_stdlib = stdET.fromstring("""<wrongnote />""")
    unknown_lxml = lxmlET.fromstring(
        """<note xml:lang="lxml test value for lang"
        o-encoding="lxml test value for encoding"
        unknown="lxml test value for unknown">lxml test value for text</note>"""
    )
    unknown_stdlib = stdET.fromstring(
        """<note xml:lang="stdlib test value for lang"
        o-encoding="stdlib test value for encoding"
        unknown="stdlib test value for unknown">stdlib test value for text</note>"""
    )

    # ==========================================================================
    #     Tests the creation of a Note
    # ==========================================================================
    def test_create_empty_note(self):
        """
        Test that an empty Note can be created
        """
        note = Note()
        assert note.lang is None
        assert note.encoding is None
        assert note.text is None
        assert note._source_elem is None

    def test_create_note_from_element(self):
        """
        Test that a Note can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        lxmlnote = Note(self.correct_lxml)
        assert lxmlnote.lang == "lxml test value for lang"
        assert lxmlnote.encoding == "lxml test value for encoding"
        assert lxmlnote.text == "lxml test value for text"
        assert lxmlnote._source_elem is self.correct_lxml
        # Check ElementTree
        stdlib_note = Note(self.correct_stdlib)
        assert stdlib_note.lang == "stdlib test value for lang"
        assert stdlib_note.encoding == "stdlib test value for encoding"
        assert stdlib_note.text == "stdlib test value for text"
        assert stdlib_note._source_elem is self.correct_stdlib

    def test_create_note_from_wrong_element_tag(self):
        """
        Test that a Note cannot be created from an element with a wrong tag
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Note(self.wrong_lxml)
        # Check ElementTree
        with pytest.raises(ValueError):
            Note(self.wrong_stdlib)

    def test_create_note_from_element_override_values(self):
        """
        Test that a Note can be created from an xml element with keyword
        arguments and that the keyword arguments override the values in the
        element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_note = Note(
            self.correct_lxml,
            text="lxml override test value for text",
            lang="lxml override test value for lang",
            encoding="lxml override test value for encoding",
        )
        assert lxml_note.text == "lxml override test value for text"
        assert lxml_note.lang == "lxml override test value for lang"
        assert lxml_note.encoding == "lxml override test value for encoding"
        assert lxml_note._source_elem is self.correct_lxml
        # Check ElementTree
        stdlib_note = Note(
            self.correct_stdlib,
            text="stdlib override test value for text",
            lang="stdlib override test value for lang",
            encoding="stdlib override test value for encoding",
        )
        assert stdlib_note.text == "stdlib override test value for text"
        assert stdlib_note.lang == "stdlib override test value for lang"
        assert stdlib_note.encoding == "stdlib override test value for encoding"
        assert stdlib_note._source_elem is self.correct_stdlib

    def test_create_note_from_element_with_unknown_attribute(self):
        """
        Test that a Note can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Note's __dir__()
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_note = Note(self.unknown_lxml)
        assert lxml_note.lang == "lxml test value for lang"
        assert lxml_note.encoding == "lxml test value for encoding"
        assert lxml_note.text == "lxml test value for text"
        assert lxml_note._source_elem is self.unknown_lxml
        assert "unknown" not in lxml_note.__dir__()

        # Check ElementTree
        stdlib_note = Note(self.unknown_stdlib)
        assert stdlib_note.lang == "stdlib test value for lang"
        assert stdlib_note.encoding == "stdlib test value for encoding"
        assert stdlib_note.text == "stdlib test value for text"
        assert stdlib_note._source_elem is self.unknown_stdlib
        assert "unknown" not in stdlib_note.__dir__()

    def test_create_note_with_non_string_attribute_value(self):
        """
        Test that a Note can be created with a non-string attribute value
        """
        note = Note(lang=1, encoding=2, text=3)
        assert note.lang == 1
        assert note.encoding == 2
        assert note.text == 3

    # ==========================================================================
    #     Tests the export of a Note
    # ==========================================================================
    def test_export_empty_note(self):
        """
        Test that an empty Note cannot be exported
        """
        with pytest.raises(AttributeError):
            Note().to_element()

    def test_export_note_with_all_attributes(self):
        """
        Test that a Note can be exported with all its attributes
        """
        note = Note(
            lang="test value for lang",
            encoding="test value for encoding",
            text="test value for text",
        )
        elem = note.to_element()
        assert elem.tag == "note"
        assert len(elem) == 0
        assert (
            elem.get("{http://www.w3.org/XML/1998/namespace}lang")
            == "test value for lang"
        )
        assert elem.get("o-encoding") == "test value for encoding"
        assert elem.text == "test value for text"

    def test_export_note_from_element(self):
        """
        Test that a Note can be created from an xml element and is the same
        as the original
        Test both lxml and stdlib
        """
        # Check lxml
        note = Note(self.correct_lxml)
        new_lxml_elem = note.to_element()
        assert new_lxml_elem.tag == new_lxml_elem.tag
        assert len(self.correct_lxml) == len(new_lxml_elem)
        assert new_lxml_elem.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        ) == self.correct_lxml.get("{http://www.w3.org/XML/1998/namespace}lang")
        assert new_lxml_elem.get("o-encoding") == self.correct_lxml.get("o-encoding")
        assert new_lxml_elem.text == self.correct_lxml.text
        # Check ElementTree
        note = Note(self.correct_stdlib)
        new_stdlib_elem = note.to_element()
        assert new_stdlib_elem.tag == self.correct_stdlib.tag
        assert len(self.correct_stdlib) == len(new_stdlib_elem)
        assert new_stdlib_elem.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        ) == self.correct_stdlib.get("{http://www.w3.org/XML/1998/namespace}lang")
        assert new_stdlib_elem.get("o-encoding") == self.correct_stdlib.get(
            "o-encoding"
        )
        assert new_stdlib_elem.text == self.correct_stdlib.text

    def test_export_note_missing_required_attributes(self):
        """
        Test that a Note cannot be exported if it is missing required attributes
        """
        note = Note(
            lang="test value for lang",
            encoding="test value for encoding",
        )
        with pytest.raises(AttributeError):
            note.to_element()

    def test_export_note_with_non_string_attributes(self):
        """
        Test that a Note cannot be exported with non-string attributes
        """
        note = Note(
            lang=1,
            encoding=2,
            text=3,
        )
        with pytest.raises(TypeError):
            note.to_element()
