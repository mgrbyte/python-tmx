import xml.etree.ElementTree as stdET
from collections import Counter, deque
from datetime import datetime

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Header, Map, Note, Prop, Ude


class TestCreateHeader:
    correct_lxml = lxmlET.fromstring(
        """<header
        creationtool="lxml creationtool"
        creationtoolversion="lxml creationtoolversion"
        datatype="lxml datatype"
        segtype="sentence"
        adminlang="lxml adminlang"
        srclang="lxml srclang"
        o-tmf="lxml tmf"
        creationdate="20020101T163812Z"
        creationid="lxml creationid"
        changedate="20020413T023401Z"
        changeid="lxml changeid"
        o-encoding="lxml encoding">
          <note>lxml note text</note>
          <prop type="lxml prop type">lxml prop text</prop>
          <ude name="lxml ude name" base="lxml ude base">
            <map unicode="lxml map unicode" code="lxml map code" ent="lxml map ent" subst="lxml map subst"/>
          </ude>
        </header>"""
    )
    correct_stdlib = stdET.fromstring(
        """<header
        creationtool="stdlib creationtool"
        creationtoolversion="stdlib creationtoolversion"
        datatype="stdlib datatype"
        segtype="sentence"
        adminlang="stdlib adminlang"
        srclang="stdlib srclang"
        o-tmf="stdlib tmf"
        creationdate="20020101T163812Z"
        creationid="stdlib creationid"
        changedate="20020413T023401Z"
        changeid="stdlib changeid"
        o-encoding="stdlib encoding">
          <note>stdlib note text</note>
          <prop type="stdlib prop type">stdlib prop text</prop>
          <ude name="stdlib ude name" base="stdlib ude base">
            <map unicode="stdlib map unicode" code="stdlib map code" ent="stdlib map ent" subst="stdlib map subst"/>
          </ude>
        </header>"""
    )
    wrong_lxml = lxmlET.fromstring("""<wrongheader />""")
    wrong_stdlib = stdET.fromstring("""<wrongheader />""")
    unknown_lxml = lxmlET.fromstring(
        """<header
        unknown="lxml unknown"
        creationtool="lxml creationtool"
        creationtoolversion="lxml creationtoolversion"
        datatype="lxml datatype"
        segtype="sentence"
        adminlang="lxml adminlang"
        srclang="lxml srclang"
        o-tmf="lxml tmf"
        creationdate="20020101T163812Z"
        creationid="lxml creationid"
        changedate="20020413T023401Z"
        changeid="lxml changeid"
        o-encoding="lxml encoding">
          <note>lxml note text</note>
          <prop type="lxml prop type">lxml prop text</prop>
          <ude name="lxml ude name" base="lxml ude base">
            <map unicode="lxml map unicode" code="lxml map code" ent="lxml map ent" subst="lxml map subst"/>
          </ude>
        </header>"""
    )
    unknown_stdlib = stdET.fromstring(
        """<header
        unknown="stdlib unknown"
        creationtool="stdlib creationtool"
        creationtoolversion="stdlib creationtoolversion"
        datatype="stdlib datatype"
        segtype="sentence"
        adminlang="stdlib adminlang"
        srclang="stdlib srclang"
        o-tmf="stdlib tmf"
        creationdate="20020101T163812Z"
        creationid="stdlib creationid"
        changedate="20020413T023401Z"
        changeid="stdlib changeid"
        o-encoding="stdlib encoding">
          <note>stdlib note text</note>
          <prop type="stdlib prop type">stdlib prop text</prop>
          <ude name="stdlib ude name" base="stdlib ude base">
            <map unicode="stdlib map unicode" code="stdlib map code" ent="stdlib map ent" subst="stdlib map subst"/>
          </ude>
        </header>"""
    )

    def test_create_empty_header(self):
        """
        Test that an empty header can be created
        """
        header = Header()
        assert header.creationtool is None
        assert header.creationtoolversion is None
        assert header.segtype is None
        assert header.tmf is None
        assert header.adminlang is None
        assert header.srclang is None
        assert header.datatype is None
        assert header.encoding is None
        assert header.creationdate is None
        assert header.creationid is None
        assert header.changedate is None
        assert header.changeid is None
        assert header.notes == []
        assert header.props == []
        assert header.udes == []

    def test_create_header_from_element(self):
        """
        Test that a Prop can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_header = Header(self.correct_lxml)
        assert lxml_header.creationtool == "lxml creationtool"
        assert lxml_header.creationtoolversion == "lxml creationtoolversion"
        assert lxml_header.segtype == "sentence"
        assert lxml_header.tmf == "lxml tmf"
        assert lxml_header.adminlang == "lxml adminlang"
        assert lxml_header.srclang == "lxml srclang"
        assert lxml_header.datatype == "lxml datatype"
        assert lxml_header.encoding == "lxml encoding"
        assert lxml_header.creationdate == datetime(2002, 1, 1, 16, 38, 12)
        assert lxml_header.creationid == "lxml creationid"
        assert lxml_header.changedate == datetime(2002, 4, 13, 2, 34, 1)
        assert lxml_header.changeid == "lxml changeid"
        assert isinstance(lxml_header.notes, list)
        assert len(lxml_header.notes) == 1
        assert isinstance(lxml_header.notes[0], Note)
        assert lxml_header.notes[0].text == "lxml note text"
        assert isinstance(lxml_header.props, list)
        assert len(lxml_header.props) == 1
        assert isinstance(lxml_header.props[0], Prop)
        assert lxml_header.props[0].type == "lxml prop type"
        assert lxml_header.props[0].text == "lxml prop text"
        assert isinstance(lxml_header.udes, list)
        assert len(lxml_header.udes) == 1
        assert isinstance(lxml_header.udes[0], Ude)
        assert lxml_header.udes[0].name == "lxml ude name"
        assert lxml_header.udes[0].base == "lxml ude base"
        assert isinstance(lxml_header.udes[0].maps, list)
        assert len(lxml_header.udes[0].maps) == 1
        assert isinstance(lxml_header.udes[0].maps[0], Map)
        assert lxml_header.udes[0].maps[0].unicode == "lxml map unicode"
        assert lxml_header.udes[0].maps[0].code == "lxml map code"
        assert lxml_header.udes[0].maps[0].ent == "lxml map ent"
        assert lxml_header.udes[0].maps[0].subst == "lxml map subst"

        # Check ElementTree
        stdlib_header = Header(self.correct_stdlib)
        assert stdlib_header.creationtool == "stdlib creationtool"
        assert stdlib_header.creationtoolversion == "stdlib creationtoolversion"
        assert stdlib_header.segtype == "sentence"
        assert stdlib_header.tmf == "stdlib tmf"
        assert stdlib_header.adminlang == "stdlib adminlang"
        assert stdlib_header.srclang == "stdlib srclang"
        assert stdlib_header.datatype == "stdlib datatype"
        assert stdlib_header.encoding == "stdlib encoding"
        assert stdlib_header.creationdate == datetime(2002, 1, 1, 16, 38, 12)
        assert stdlib_header.creationid == "stdlib creationid"
        assert stdlib_header.changedate == datetime(2002, 4, 13, 2, 34, 1)
        assert stdlib_header.changeid == "stdlib changeid"
        assert isinstance(stdlib_header.notes, list)
        assert len(stdlib_header.notes) == 1
        assert isinstance(stdlib_header.notes[0], Note)
        assert stdlib_header.notes[0].text == "stdlib note text"
        assert isinstance(stdlib_header.props, list)
        assert len(stdlib_header.props) == 1
        assert isinstance(stdlib_header.props[0], Prop)
        assert stdlib_header.props[0].type == "stdlib prop type"
        assert stdlib_header.props[0].text == "stdlib prop text"
        assert isinstance(stdlib_header.udes, list)
        assert len(stdlib_header.udes) == 1
        assert isinstance(stdlib_header.udes[0], Ude)
        assert stdlib_header.udes[0].name == "stdlib ude name"
        assert stdlib_header.udes[0].base == "stdlib ude base"
        assert isinstance(stdlib_header.udes[0].maps, list)
        assert len(stdlib_header.udes[0].maps) == 1
        assert isinstance(stdlib_header.udes[0].maps[0], Map)
        assert stdlib_header.udes[0].maps[0].unicode == "stdlib map unicode"
        assert stdlib_header.udes[0].maps[0].code == "stdlib map code"
        assert stdlib_header.udes[0].maps[0].ent == "stdlib map ent"
        assert stdlib_header.udes[0].maps[0].subst == "stdlib map subst"

    def test_create_header_from_wrong_element_tag(self):
        """
        Test that a Header cannot be created from an element with a wrong tag
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Header(self.wrong_lxml)
        # Check ElementTree
        with pytest.raises(ValueError):
            Header(self.wrong_stdlib)

    def test_create_header_from_element_override_values(self):
        """
        Test that a Header can be created from an xml element with keyword
        arguments and that the keyword arguments override the values in the
        element
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_header = Header(
            self.correct_lxml,
            creationtool="override lxml creationtool",
            creationtoolversion="override lxml creationtoolversion",
            segtype="override lxml segtype",
            tmf="override lxml tmf",
            adminlang="override lxml adminlang",
            srclang="override lxml srclang",
            datatype="override lxml datatype",
            encoding="override lxml encoding",
            creationdate=datetime(2024, 11, 14, 17, 43, 12),
            creationid="override lxml creationid",
            changedate=datetime(2024, 11, 15, 18, 24, 10),
            changeid="override lxml changeid",
            notes=[
                Note(
                    self.correct_lxml.find("note"),
                    text="override lxml note text",
                    lang="override lxml note lang",
                    encoding="override lxml note encoding",
                )
            ],
            props=[
                Prop(
                    self.correct_lxml.find("prop"),
                    text="override lxml prop text",
                    type="override lxml prop type",
                    lang="override lxml prop lang",
                    encoding="override lxml prop encoding",
                )
            ],
            udes=[
                Ude(
                    self.correct_lxml.find("ude"),
                    name="override lxml ude name",
                    base="override lxml ude base",
                    maps=[
                        Map(
                            self.correct_lxml.find("map"),
                            unicode="override lxml map unicode",
                            code="override lxml map code",
                            ent="override lxml map ent",
                            subst="override lxml map subst",
                        )
                    ],
                )
            ],
        )
        assert lxml_header.creationtool == "override lxml creationtool"
        assert lxml_header.creationtoolversion == "override lxml creationtoolversion"
        assert lxml_header.segtype == "override lxml segtype"
        assert lxml_header.tmf == "override lxml tmf"
        assert lxml_header.adminlang == "override lxml adminlang"
        assert lxml_header.srclang == "override lxml srclang"
        assert lxml_header.datatype == "override lxml datatype"
        assert lxml_header.encoding == "override lxml encoding"
        assert lxml_header.creationdate == datetime(2024, 11, 14, 17, 43, 12)
        assert lxml_header.creationid == "override lxml creationid"
        assert lxml_header.changedate == datetime(2024, 11, 15, 18, 24, 10)
        assert lxml_header.changeid == "override lxml changeid"
        assert isinstance(lxml_header.notes, list)
        assert len(lxml_header.notes) == 1
        assert isinstance(lxml_header.notes[0], Note)
        assert lxml_header.notes[0].text == "override lxml note text"
        assert lxml_header.notes[0].lang == "override lxml note lang"
        assert lxml_header.notes[0].encoding == "override lxml note encoding"
        assert isinstance(lxml_header.props, list)
        assert len(lxml_header.props) == 1
        assert isinstance(lxml_header.props[0], Prop)
        assert lxml_header.props[0].type == "override lxml prop type"
        assert lxml_header.props[0].text == "override lxml prop text"
        assert lxml_header.props[0].lang == "override lxml prop lang"
        assert lxml_header.props[0].encoding == "override lxml prop encoding"
        assert isinstance(lxml_header.udes, list)
        assert len(lxml_header.udes) == 1
        assert isinstance(lxml_header.udes[0], Ude)
        assert lxml_header.udes[0].name == "override lxml ude name"
        assert lxml_header.udes[0].base == "override lxml ude base"
        assert isinstance(lxml_header.udes[0].maps, list)
        assert len(lxml_header.udes[0].maps) == 1
        assert isinstance(lxml_header.udes[0].maps[0], Map)
        assert lxml_header.udes[0].maps[0].unicode == "override lxml map unicode"
        assert lxml_header.udes[0].maps[0].code == "override lxml map code"
        assert lxml_header.udes[0].maps[0].ent == "override lxml map ent"
        assert lxml_header.udes[0].maps[0].subst == "override lxml map subst"

        # Check ElementTree
        stdlib_header = Header(
            self.correct_stdlib,
            creationtool="override stdlib creationtool",
            creationtoolversion="override stdlib creationtoolversion",
            segtype="override stdlib segtype",
            tmf="override stdlib tmf",
            adminlang="override stdlib adminlang",
            srclang="override stdlib srclang",
            datatype="override stdlib datatype",
            encoding="override stdlib encoding",
            creationdate=datetime(2023, 11, 14, 17, 43, 12),
            creationid="override stdlib creationid",
            changedate=datetime(2022, 11, 15, 18, 24, 10),
            changeid="override stdlib changeid",
            notes=[
                Note(
                    self.correct_stdlib.find("note"),
                    text="override stdlib note text",
                    lang="override stdlib note lang",
                    encoding="override stdlib note encoding",
                )
            ],
            props=[
                Prop(
                    self.correct_stdlib.find("prop"),
                    text="override stdlib prop text",
                    type="override stdlib prop type",
                    lang="override stdlib prop lang",
                    encoding="override stdlib prop encoding",
                )
            ],
            udes=[
                Ude(
                    self.correct_stdlib.find("ude"),
                    name="override stdlib ude name",
                    base="override stdlib ude base",
                    maps=[
                        Map(
                            self.correct_stdlib.find("map"),
                            unicode="override stdlib map unicode",
                            code="override stdlib map code",
                            ent="override stdlib map ent",
                            subst="override stdlib map subst",
                        )
                    ],
                )
            ],
        )
        assert stdlib_header.creationtool == "override stdlib creationtool"
        assert (
            stdlib_header.creationtoolversion == "override stdlib creationtoolversion"
        )
        assert stdlib_header.segtype == "override stdlib segtype"
        assert stdlib_header.tmf == "override stdlib tmf"
        assert stdlib_header.adminlang == "override stdlib adminlang"
        assert stdlib_header.srclang == "override stdlib srclang"
        assert stdlib_header.datatype == "override stdlib datatype"
        assert stdlib_header.encoding == "override stdlib encoding"
        assert stdlib_header.creationdate == datetime(2023, 11, 14, 17, 43, 12)
        assert stdlib_header.creationid == "override stdlib creationid"
        assert stdlib_header.changedate == datetime(2022, 11, 15, 18, 24, 10)
        assert stdlib_header.changeid == "override stdlib changeid"
        assert isinstance(stdlib_header.notes, list)
        assert len(stdlib_header.notes) == 1
        assert isinstance(stdlib_header.notes[0], Note)
        assert stdlib_header.notes[0].text == "override stdlib note text"
        assert stdlib_header.notes[0].lang == "override stdlib note lang"
        assert stdlib_header.notes[0].encoding == "override stdlib note encoding"
        assert isinstance(stdlib_header.props, list)
        assert len(stdlib_header.props) == 1
        assert isinstance(stdlib_header.props[0], Prop)
        assert stdlib_header.props[0].type == "override stdlib prop type"
        assert stdlib_header.props[0].text == "override stdlib prop text"
        assert stdlib_header.props[0].lang == "override stdlib prop lang"
        assert stdlib_header.props[0].encoding == "override stdlib prop encoding"
        assert isinstance(stdlib_header.udes, list)
        assert len(stdlib_header.udes) == 1
        assert isinstance(stdlib_header.udes[0], Ude)
        assert stdlib_header.udes[0].name == "override stdlib ude name"
        assert stdlib_header.udes[0].base == "override stdlib ude base"
        assert isinstance(stdlib_header.udes[0].maps, list)
        assert len(stdlib_header.udes[0].maps) == 1
        assert isinstance(stdlib_header.udes[0].maps[0], Map)
        assert stdlib_header.udes[0].maps[0].unicode == "override stdlib map unicode"
        assert stdlib_header.udes[0].maps[0].code == "override stdlib map code"
        assert stdlib_header.udes[0].maps[0].ent == "override stdlib map ent"
        assert stdlib_header.udes[0].maps[0].subst == "override stdlib map subst"

    def test_create_header_from_element_with_unknown_attribute(self):
        """
        Test that a Header can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Header's __dir__()
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_header = Header(self.unknown_lxml)
        assert lxml_header.creationtool == "lxml creationtool"
        assert lxml_header.creationtoolversion == "lxml creationtoolversion"
        assert lxml_header.segtype == "sentence"
        assert lxml_header.tmf == "lxml tmf"
        assert lxml_header.adminlang == "lxml adminlang"
        assert lxml_header.srclang == "lxml srclang"
        assert lxml_header.datatype == "lxml datatype"
        assert lxml_header.encoding == "lxml encoding"
        assert lxml_header.creationdate == datetime(2002, 1, 1, 16, 38, 12)
        assert lxml_header.creationid == "lxml creationid"
        assert lxml_header.changedate == datetime(2002, 4, 13, 2, 34, 1)
        assert lxml_header.changeid == "lxml changeid"
        assert isinstance(lxml_header.notes, list)
        assert len(lxml_header.notes) == 1
        assert isinstance(lxml_header.notes[0], Note)
        assert lxml_header.notes[0].text == "lxml note text"
        assert isinstance(lxml_header.props, list)
        assert len(lxml_header.props) == 1
        assert isinstance(lxml_header.props[0], Prop)
        assert lxml_header.props[0].type == "lxml prop type"
        assert lxml_header.props[0].text == "lxml prop text"
        assert isinstance(lxml_header.udes, list)
        assert len(lxml_header.udes) == 1
        assert isinstance(lxml_header.udes[0], Ude)
        assert lxml_header.udes[0].name == "lxml ude name"
        assert lxml_header.udes[0].base == "lxml ude base"
        assert isinstance(lxml_header.udes[0].maps, list)
        assert len(lxml_header.udes[0].maps) == 1
        assert isinstance(lxml_header.udes[0].maps[0], Map)
        assert lxml_header.udes[0].maps[0].unicode == "lxml map unicode"
        assert lxml_header.udes[0].maps[0].code == "lxml map code"
        assert lxml_header.udes[0].maps[0].ent == "lxml map ent"
        assert lxml_header.udes[0].maps[0].subst == "lxml map subst"
        assert "unknown" not in lxml_header.__dir__()

        # Check ElementTree
        stdlib_header = Header(self.unknown_stdlib)
        assert stdlib_header.creationtool == "stdlib creationtool"
        assert stdlib_header.creationtoolversion == "stdlib creationtoolversion"
        assert stdlib_header.segtype == "sentence"
        assert stdlib_header.tmf == "stdlib tmf"
        assert stdlib_header.adminlang == "stdlib adminlang"
        assert stdlib_header.srclang == "stdlib srclang"
        assert stdlib_header.datatype == "stdlib datatype"
        assert stdlib_header.encoding == "stdlib encoding"
        assert stdlib_header.creationdate == datetime(2002, 1, 1, 16, 38, 12)
        assert stdlib_header.creationid == "stdlib creationid"
        assert stdlib_header.changedate == datetime(2002, 4, 13, 2, 34, 1)
        assert stdlib_header.changeid == "stdlib changeid"
        assert isinstance(stdlib_header.notes, list)
        assert len(stdlib_header.notes) == 1
        assert isinstance(stdlib_header.notes[0], Note)
        assert stdlib_header.notes[0].text == "stdlib note text"
        assert isinstance(stdlib_header.props, list)
        assert len(stdlib_header.props) == 1
        assert isinstance(stdlib_header.props[0], Prop)
        assert stdlib_header.props[0].type == "stdlib prop type"
        assert stdlib_header.props[0].text == "stdlib prop text"
        assert isinstance(stdlib_header.udes, list)
        assert len(stdlib_header.udes) == 1
        assert isinstance(stdlib_header.udes[0], Ude)
        assert stdlib_header.udes[0].name == "stdlib ude name"
        assert stdlib_header.udes[0].base == "stdlib ude base"
        assert isinstance(stdlib_header.udes[0].maps, list)
        assert len(stdlib_header.udes[0].maps) == 1
        assert isinstance(stdlib_header.udes[0].maps[0], Map)
        assert stdlib_header.udes[0].maps[0].unicode == "stdlib map unicode"
        assert stdlib_header.udes[0].maps[0].code == "stdlib map code"
        assert stdlib_header.udes[0].maps[0].ent == "stdlib map ent"
        assert stdlib_header.udes[0].maps[0].subst == "stdlib map subst"
        assert "unknown" not in stdlib_header.__dir__()

    def test_create_header_with_non_string_attribute_value(self):
        """
        Test that a Header can be created with a non-string attribute value
        Had a bit of fun trying all the types I could BESIDES str
        """
        header = Header(
            creationtool=1,
            creationtoolversion=[1, 2],
            segtype={3, 4},
            tmf=5.6,
            adminlang={7: 8, 9: 10},
            srclang=(11, 12),
            datatype=complex(13, 14.15),
            encoding=datetime(2002, 1, 1, 16, 38, 12),
            creationdate=Map(),
            creationid=True,
            changedate=bytes(i for i in range(10)),
            changeid=Counter(i for i in range(10)),
            notes=frozenset([1, 2, 3]),
            props=range(10),
            udes=deque([1, 2, 3]),
        )
        assert isinstance(header.creationtool, int)
        assert isinstance(header.creationtoolversion, list)
        assert isinstance(header.segtype, set)
        assert isinstance(header.tmf, float)
        assert isinstance(header.adminlang, dict)
        assert isinstance(header.srclang, tuple)
        assert isinstance(header.datatype, complex)
        assert isinstance(header.encoding, datetime)
        assert isinstance(header.creationdate, Map)
        assert isinstance(header.creationid, bool)
        assert isinstance(header.changedate, bytes)
        assert isinstance(header.changeid, Counter)
        assert isinstance(header.notes, frozenset)
        assert isinstance(header.props, range)
        assert isinstance(header.udes, deque)
        assert header.creationtool == 1
        assert header.creationtoolversion == [1, 2]
        assert header.segtype == {3, 4}
        assert header.tmf == 5.6
        assert header.adminlang == {7: 8, 9: 10}
        assert header.srclang == (11, 12)
        assert header.datatype == complex(13, 14.15)
        assert header.encoding == datetime(2002, 1, 1, 16, 38, 12)
        assert header.creationdate == Map()
        assert header.creationid is True
        assert header.changedate == bytes(i for i in range(10))
        assert header.changeid == Counter(i for i in range(10))
        assert header.notes == frozenset([1, 2, 3])
        assert header.props == range(10)
        assert header.udes == deque([1, 2, 3])

    # ==========================================================================
    #     Tests the export of a Header
    # ==========================================================================
    def test_export_empty_header(self):
        """
        Test that an empty Header cannot be exported
        """
        with pytest.raises(AttributeError):
            Header().to_element()

    def test_export_header_with_all_attributes(self):
        """
        Test that a Header can be exported with all its attributes
        """
        header = Header(
            creationtool="test value for creationtool",
            creationtoolversion="test value for creationtoolversion",
            segtype="sentence",
            tmf="test value for tmf",
            adminlang="test value for adminlang",
            srclang="test value for srclang",
            datatype="test value for datatype",
            encoding="test value for encoding",
            creationdate=datetime(2002, 1, 1, 16, 38, 12),
            creationid="test value for creationid",
            changedate=datetime(2002, 4, 13, 2, 34, 1),
            changeid="test value for changeid",
            notes=[
                Note(
                    text="test value for note text",
                    lang="test value for note lang",
                    encoding="test value for note encoding",
                )
            ],
            props=[
                Prop(
                    text="test value for prop text",
                    type="test value for prop type",
                    lang="test value for prop lang",
                    encoding="test value for prop encoding",
                )
            ],
            udes=[
                Ude(
                    name="test value for ude name",
                    base="test value for ude base",
                    maps=[
                        Map(
                            unicode="test value for map unicode",
                            code="test value for map code",
                            ent="test value for map ent",
                            subst="test value for map subst",
                        )
                    ],
                )
            ],
        )
        elem = header.to_element()
        assert elem.tag == "header"
        assert len(elem) == 3
        assert elem.get("creationtool") == "test value for creationtool"
        assert elem.get("creationtoolversion") == "test value for creationtoolversion"
        assert elem.get("segtype") == "sentence"
        assert elem.get("o-tmf") == "test value for tmf"
        assert elem.get("adminlang") == "test value for adminlang"
        assert elem.get("srclang") == "test value for srclang"
        assert elem.get("datatype") == "test value for datatype"
        assert elem.get("o-encoding") == "test value for encoding"
        assert elem.get("creationdate") == "20020101T163812Z"
        assert elem.get("creationid") == "test value for creationid"
        assert elem.get("changedate") == "20020413T023401Z"
        assert elem.get("changeid") == "test value for changeid"
        assert len(elem.findall("note")) == 1
        assert len(elem.findall("prop")) == 1
        assert len(elem.findall("ude")) == 1
        assert elem.find("note").text == "test value for note text"
        assert elem.find("prop").text == "test value for prop text"
        assert elem.find("prop").get("type") == "test value for prop type"
        assert elem.find("ude").get("name") == "test value for ude name"
        assert elem.find("ude").get("base") == "test value for ude base"
        assert len(elem.find("ude").findall("map")) == 1
        assert (
            elem.find("ude").find("map").get("unicode") == "test value for map unicode"
        )
        assert elem.find("ude").find("map").get("code") == "test value for map code"
        assert elem.find("ude").find("map").get("ent") == "test value for map ent"
        assert elem.find("ude").find("map").get("subst") == "test value for map subst"

    def test_export_header_from_element(self):
        """
        Test that a Header can be created from an xml element and is the same
        as the original
        Test both lxml and stdlib
        """
        # Check lxml
        lxml_header = Header(self.correct_lxml)
        new_lxml_elem = lxml_header.to_element()
        assert new_lxml_elem.tag == new_lxml_elem.tag
        assert len(self.correct_lxml) == len(new_lxml_elem)
        for k, v in self.correct_lxml.attrib.items():
            assert new_lxml_elem.get(k) == v
        assert new_lxml_elem.find("note").text == self.correct_lxml.find("note").text
        assert new_lxml_elem.find("prop").text == self.correct_lxml.find("prop").text
        assert new_lxml_elem.find("prop").get("type") == self.correct_lxml.find(
            "prop"
        ).get("type")
        assert new_lxml_elem.find("ude").get("name") == self.correct_lxml.find(
            "ude"
        ).get("name")
        assert new_lxml_elem.find("ude").get("base") == self.correct_lxml.find(
            "ude"
        ).get("base")
        assert len(new_lxml_elem.find("ude").findall("map")) == len(
            self.correct_lxml.find("ude").findall("map")
        )
        assert new_lxml_elem.find("ude").find("map").get(
            "unicode"
        ) == self.correct_lxml.find("ude").find("map").get("unicode")
        assert new_lxml_elem.find("ude").find("map").get(
            "code"
        ) == self.correct_lxml.find("ude").find("map").get("code")
        assert new_lxml_elem.find("ude").find("map").get(
            "ent"
        ) == self.correct_lxml.find("ude").find("map").get("ent")
        assert new_lxml_elem.find("ude").find("map").get(
            "subst"
        ) == self.correct_lxml.find("ude").find("map").get("subst")
        # Check ElementTree
        stdlib_header = Header(self.correct_stdlib)
        new_stdlib_elem = stdlib_header.to_element()
        assert new_stdlib_elem.tag == new_stdlib_elem.tag
        assert len(self.correct_stdlib) == len(new_stdlib_elem)
        for k, v in self.correct_stdlib.attrib.items():
            assert new_stdlib_elem.get(k) == v
        assert (
            new_stdlib_elem.find("note").text == self.correct_stdlib.find("note").text
        )
        assert (
            new_stdlib_elem.find("prop").text == self.correct_stdlib.find("prop").text
        )
        assert new_stdlib_elem.find("prop").get("type") == self.correct_stdlib.find(
            "prop"
        ).get("type")
        assert new_stdlib_elem.find("ude").get("name") == self.correct_stdlib.find(
            "ude"
        ).get("name")
        assert new_stdlib_elem.find("ude").get("base") == self.correct_stdlib.find(
            "ude"
        ).get("base")
        assert len(new_stdlib_elem.find("ude").findall("map")) == len(
            self.correct_stdlib.find("ude").findall("map")
        )
        assert new_stdlib_elem.find("ude").find("map").get(
            "unicode"
        ) == self.correct_stdlib.find("ude").find("map").get("unicode")
        assert new_stdlib_elem.find("ude").find("map").get(
            "code"
        ) == self.correct_stdlib.find("ude").find("map").get("code")
        assert new_stdlib_elem.find("ude").find("map").get(
            "ent"
        ) == self.correct_stdlib.find("ude").find("map").get("ent")
        assert new_stdlib_elem.find("ude").find("map").get(
            "subst"
        ) == self.correct_stdlib.find("ude").find("map").get("subst")

    def test_export_header_missing_required_attributes(self):
        """
        Test that a Header cannot be exported if it is missing required attributes
        """
        header = Header(
            encoding="test value for encoding",
            creationdate=datetime(2002, 1, 1, 16, 38, 12),
            creationid="test value for creationid",
            changedate=datetime(2002, 4, 13, 2, 34, 1),
            changeid="test value for changeid",
            notes=[
                Note(
                    text="test value for note text",
                    lang="test value for note lang",
                    encoding="test value for note encoding",
                )
            ],
            props=[
                Prop(
                    text="test value for prop text",
                    type="test value for prop type",
                    lang="test value for prop lang",
                    encoding="test value for prop encoding",
                )
            ],
            udes=[
                Ude(
                    name="test value for ude name",
                    base="test value for ude base",
                    maps=[
                        Map(
                            unicode="test value for map unicode",
                            code="test value for map code",
                            ent="test value for map ent",
                            subst="test value for map subst",
                        )
                    ],
                )
            ],
        )
        with pytest.raises(AttributeError):
            header.to_element()

    def test_export_header_with_non_string_attributes(self):
        """
        Test that a Header cannot be exported with non-string attributes
        """
        header = Header(
            creationtool=1,
            creationtoolversion=[1, 2],
            segtype={3, 4},
            tmf=5.6,
            adminlang={7: 8, 9: 10},
            srclang=(11, 12),
            datatype=complex(13, 14.15),
            encoding=datetime(2002, 1, 1, 16, 38, 12),
            creationdate=Map(),
            creationid=True,
            changedate=bytes(i for i in range(10)),
            changeid=Counter(i for i in range(10)),
            notes=frozenset([1, 2, 3]),
            props=range(10),
            udes=deque([1, 2, 3]),
        )
        with pytest.raises(TypeError):
            header.to_element()
