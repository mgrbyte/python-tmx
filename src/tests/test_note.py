from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Note


class TestNote(TestCase):
    def test_create_export_empty_note(self):
        note = Note()
        for attr in note.__slots__:
            self.assertIsNone(getattr(note, attr))
        with self.assertRaises(AttributeError):
            note.to_element()

    def test_create_note_from_element(self):
        elem = fromstring(
            """<note xml:lang="en-US" o-encoding="utf-8" >note text</note>"""
        )
        note = Note(elem)
        self.assertEqual(note._source_elem, elem)
        self.assertEqual(note.text, elem.text)
        self.assertEqual(
            note.lang, elem.get("{http://www.w3.org/XML/1998/namespace}lang")
        )
        self.assertEqual(note.encoding, elem.get("o-encoding"))

    def test_export_minimal_note(self):
        note = Note(text="note text")
        elem = note.to_element()
        self.assertEqual(elem.text, note.text)
        self.assertEqual(elem.tag, "note")
        self.assertEqual(len(elem), 0)
        self.assertEqual(len(elem.attrib), 0)

    def test_add_unknown_attributes(self):
        note = Note()
        with self.assertRaises(AttributeError):
            note.other = "test"

    def test_create_note_from_element_with_unknwon_attributes(self):
        elem = fromstring("""<note other="other"/>""")
        new_note = Note(elem)
        self.assertNotIn("other", new_note.__dir__())

    def test_create_note_from_element_with_kwargs(self):
        note = Note(
            fromstring(
                """<note xml:lang="en-US" o-encoding="utf-8">note text</note>"""
            ),
            text="override text",
        )
        self.assertEqual(note.text, "override text")
        self.assertEqual(note.lang, "en-US")
        self.assertEqual(note.encoding, "utf-8")

    def test_use_note_dunder_methods(self):
        note = Note()
        note.text = "text"
        self.assertEqual(note.text, note["text"])
        note["text"] = "new text"
        self.assertEqual(note["text"], "new text")
        with self.assertRaises(KeyError):
            note["unknown"]
        with self.assertRaises(KeyError):
            note["unknown"] = "test"
        del note["text"]
        self.assertIsNone(note.text)

    def test_create_note_from_element_wrong_tag(self):
        with self.assertRaises(ValueError):
            Note(fromstring("<wrong_tag/>"))

    def test_export_note_wrong_attribute_type(self):
        note = Note()
        note.text = 123
        with self.assertRaises(TypeError):
            note.to_element()
