"""
Tests for the Header class
"""

from datetime import datetime
from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Header, Map, Note, Prop, Ude


class TestHeader(TestCase):
    def test_empty_header(self):
        header = Header()
        self.assertIsNone(header._source_elem)
        self.assertIsNone(header.creationtool)
        self.assertIsNone(header.creationtoolversion)
        self.assertIsNone(header.segtype)
        self.assertIsNone(header.tmf)
        self.assertIsNone(header.adminlang)
        self.assertIsNone(header.srclang)
        self.assertIsNone(header.datatype)
        self.assertIsNone(header.encoding)
        self.assertIsNone(header.creationdate)
        self.assertIsNone(header.creationid)
        self.assertIsNone(header.changedate)
        self.assertIsNone(header.changeid)
        self.assertEqual(len(header.notes), 0)
        self.assertEqual(len(header.props), 0)
        self.assertEqual(len(header.udes), 0)
        with self.assertRaises(AttributeError):
            header.to_element()

    def test_header_from_element(self):
        elem = fromstring(
            """<header
            creationtool="creationtool"
            creationtoolversion="creationtoolversion"
            datatype="datatype"
            segtype="sentence"
            adminlang="adminlang"
            srclang="srclang"
            o-tmf="tmf"
            creationdate="20020101T163812Z"
            creationid="creationid"
            changedate="20020413T023401Z"
            changeid="changeid"
            o-encoding="encoding">
              <note>note text</note>
              <prop type="prop type">prop text</prop>
              <ude name="name" base="base">
                <map unicode="unicode" code="code" ent="ent" subst="subst"/>
              </ude>
            </header>"""
        )
        header = Header(elem)
        self.assertEqual(header._source_elem, elem)
        self.assertEqual(header.creationtool, elem.get("creationtool"))
        self.assertEqual(header.creationtoolversion, elem.get("creationtoolversion"))
        self.assertEqual(header.segtype, elem.get("segtype"))
        self.assertEqual(header.tmf, elem.get("o-tmf"))
        self.assertEqual(header.adminlang, elem.get("adminlang"))
        self.assertEqual(header.srclang, elem.get("srclang"))
        self.assertEqual(header.datatype, elem.get("datatype"))
        self.assertEqual(header.encoding, elem.get("o-encoding"))
        self.assertEqual(header.creationdate, datetime(2002, 1, 1, 16, 38, 12))
        self.assertEqual(header.creationid, elem.get("creationid"))
        self.assertEqual(header.changedate, datetime(2002, 4, 13, 2, 34, 1))
        self.assertEqual(header.changeid, elem.get("changeid"))
        self.assertEqual(len(header.notes), 1)
        self.assertEqual(len(header.props), 1)
        self.assertEqual(len(header.udes), 1)
        self.assertIsInstance(header.notes[0], Note)
        self.assertEqual(header.notes[0].text, elem.find("note").text)
        self.assertIsNone(header.notes[0].lang)
        self.assertIsNone(header.notes[0].encoding)
        self.assertIsInstance(header.props[0], Prop)
        self.assertIsNone(header.props[0].lang)
        self.assertIsNone(header.props[0].encoding)
        self.assertEqual(header.props[0].type, elem.find("prop").get("type"))
        self.assertEqual(header.props[0].text, elem.find("prop").text)
        self.assertIsInstance(header.udes[0], Ude)
        self.assertEqual(header.udes[0].name, elem.find("ude").get("name"))
        self.assertEqual(header.udes[0].base, elem.find("ude").get("base"))
        self.assertEqual(len(header.udes[0].maps), 1)
        self.assertIsInstance(header.udes[0].maps[0], Map)
        self.assertEqual(
            header.udes[0].maps[0].unicode, elem.find("ude").find("map").get("unicode")
        )
        self.assertEqual(
            header.udes[0].maps[0].code, elem.find("ude").find("map").get("code")
        )
        self.assertEqual(
            header.udes[0].maps[0].ent, elem.find("ude").find("map").get("ent")
        )
        self.assertEqual(
            header.udes[0].maps[0].subst, elem.find("ude").find("map").get("subst")
        )

    def test_create_header_from_element(self):
        elem = fromstring(
            """<header
            creationtool="creationtool"
            creationtoolversion="creationtoolversion"
            datatype="datatype"
            segtype="sentence"
            adminlang="adminlang"
            srclang="srclang"
            o-tmf="tmf"
            creationdate="20020101T163812Z"
            creationid="creationid"
            changedate="20020413T023401Z"
            changeid="changeid"
            o-encoding="encoding">
              <note>note text</note>
              <prop type="prop type">prop text</prop>
              <ude name="ude name" base="ude base">
                <map unicode="map unicode" code="map code" ent="map ent" subst="map subst"/>
              </ude>
            </header>"""
        )
        header = Header(elem)
        self.assertEqual(header._source_elem, elem)
        self.assertEqual(header.creationtool, elem.get("creationtool"))
        self.assertEqual(header.creationtoolversion, elem.get("creationtoolversion"))
        self.assertEqual(header.segtype, elem.get("segtype"))
        self.assertEqual(header.tmf, elem.get("o-tmf"))
        self.assertEqual(header.adminlang, elem.get("adminlang"))
        self.assertEqual(header.srclang, elem.get("srclang"))
        self.assertEqual(header.datatype, elem.get("datatype"))
        self.assertEqual(header.encoding, elem.get("o-encoding"))
        self.assertEqual(header.creationdate, datetime(2002, 1, 1, 16, 38, 12))
        self.assertEqual(header.creationid, elem.get("creationid"))
        self.assertEqual(header.changedate, datetime(2002, 4, 13, 2, 34, 1))
        self.assertEqual(header.changeid, elem.get("changeid"))
        self.assertEqual(len(header.notes), 1)
        self.assertEqual(len(header.props), 1)
        self.assertEqual(len(header.udes), 1)
        self.assertIsInstance(header.notes[0], Note)
        self.assertEqual(header.notes[0].text, elem.find("note").text)
        self.assertIsInstance(header.props[0], Prop)
        self.assertEqual(header.props[0].type, elem.find("prop").get("type"))
        self.assertEqual(header.props[0].text, elem.find("prop").text)
        self.assertIsInstance(header.udes[0], Ude)
        self.assertEqual(header.udes[0].name, elem.find("ude").get("name"))
        self.assertEqual(header.udes[0].base, elem.find("ude").get("base"))
        self.assertEqual(len(header.udes[0].maps), 1)
        self.assertIsInstance(header.udes[0].maps[0], Map)
        self.assertEqual(
            header.udes[0].maps[0].unicode, elem.find("ude").find("map").get("unicode")
        )
        self.assertEqual(
            header.udes[0].maps[0].code, elem.find("ude").find("map").get("code")
        )
        self.assertEqual(
            header.udes[0].maps[0].ent, elem.find("ude").find("map").get("ent")
        )
        self.assertEqual(
            header.udes[0].maps[0].subst, elem.find("ude").find("map").get("subst")
        )
