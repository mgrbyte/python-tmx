"""
Tests for the Note class
"""

from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Note


class TestNote(TestCase):
    def test_empty_note(self):
        note = Note()
        self.assertIsNone(note._source_elem)
        self.assertIsNone(note.lang)
        self.assertIsNone(note.encoding)
        self.assertIsNone(note.text)
        with self.assertRaises(AttributeError):
            note.to_element()

    def test_note_from_element(self):
        elem = fromstring("""<note xml:lang="lang" o-encoding="encoding">text</note>""")
        note = Note(elem)
        self.assertEqual(note._source_elem, elem)
        self.assertEqual(
            note.lang, elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.assertEqual(note.encoding, elem.get("o-encoding"))
        self.assertEqual(note.text, elem.text)
        new_elem = note.to_element()
        self.assertEqual(
            new_elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
            elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
        )
        self.assertEqual(new_elem.get("o-encoding"), elem.get("o-encoding"))
        self.assertEqual(new_elem.text, elem.text)

    def test_unknown_attributes(self):
        note = Note()
        with self.assertRaises(AttributeError):
            note.other = "test"
        self.assertIsNone(note._source_elem)
        self.assertIsNone(note.lang)
        self.assertIsNone(note.encoding)
        self.assertIsNone(note.text)

        elem = fromstring("""<note other="other"/>""")
        new_note = Note(elem)
        self.assertNotIn("other", new_note.__dir__())
        self.assertEqual(new_note._source_elem, elem)
        self.assertIsNone(new_note.lang)
        self.assertIsNone(new_note.encoding)
        self.assertIsNone(new_note.text)

        note.text = 1337
        with self.assertRaises(TypeError):
            note.to_element()
        note.text = None
        with self.assertRaises(AttributeError):
            note.to_element()

    def test_create_note_from_element_with_kwargs(self):
        elem = fromstring("""<note o-encoding="encoding">text</note>""")
        note = Note(elem, lang="override lang", encoding="override encoding")
        self.assertEqual(note._source_elem, elem)
        self.assertEqual(note.lang, "override lang")
        self.assertEqual(note.encoding, "override encoding")
        self.assertEqual(note.text, elem.text)
