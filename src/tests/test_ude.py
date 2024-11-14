import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Map, Ude


class TestCreateUde:
    correct_lxml = lxmlET.fromstring(
        """<ude name="lxml test value for name" base="lxml test value for base">
        <map unicode="lxml test value for unicode 1" code="lxml test value for code 1"/>
        <map unicode="lxml test value for unicode 2" code="lxml test value for code 2"/>
        </ude>"""
    )
    correct_stdlib = stdET.fromstring(
        """<ude name="stdlib test value for name" base="stdlib test value for base">
        <map unicode="stdlib test value for unicode 1" code="stdlib test value for code 1"/>
        <map unicode="stdlib test value for unicode 2" code="stdlib test value for code 2"/>
        </ude>"""
    )
    wrong_lxml = lxmlET.fromstring("""<wrongude />""")
    wrong_stdlib = stdET.fromstring("""<wrongude />""")
    unknown_lxml = lxmlET.fromstring(
        """<ude name="lxml test value for name" base="lxml test value for base"
        unknown="should not appear">
        <map unicode="lxml test value for unicode 1" code="lxml test value for code 1"/>
        <map unicode="lxml test value for unicode 2" code="lxml test value for code 2"/>
        </ude>"""
    )
    unknown_stdlib = stdET.fromstring(
        """<ude name="stdlib test value for name" base="stdlib test value for base"
        unknown="should not appear">
        <map unicode="stdlib test value for unicode 1" code="stdlib test value for code 1"/>
        <map unicode="stdlib test value for unicode 2" code="stdlib test value for code 2"/>
        </ude>"""
    )

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

    def test_create_ude_from_element(self):
        """
        Test that a Ude can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        ude = Ude(self.correct_lxml)
        assert ude.base == "lxml test value for base"
        assert ude.name == "lxml test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "lxml test value for unicode 1"
        assert ude.maps[0].code == "lxml test value for code 1"
        assert ude.maps[1].unicode == "lxml test value for unicode 2"
        assert ude.maps[1].code == "lxml test value for code 2"

        # Check ElementTree
        ude = Ude(self.correct_stdlib)
        assert ude.base == "stdlib test value for base"
        assert ude.name == "stdlib test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "stdlib test value for unicode 1"
        assert ude.maps[0].code == "stdlib test value for code 1"
        assert ude.maps[1].unicode == "stdlib test value for unicode 2"
        assert ude.maps[1].code == "stdlib test value for code 2"

    def test_create_ude_from_wrong_element_tag(self):
        """
        Test that a Ude cannot be created from an element with a wrong tag
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Ude(self.wrong_lxml)

        # Check ElementTree
        with pytest.raises(ValueError):
            Ude(self.wrong_stdlib)

    def test_create_ude_from_element_override_values(self):
        """
        Test that a Ude can be created from an xml element with keyword
        arguments
        Test both lxml and stdlib
        """
        # Check lxml
        ude = Ude(
            self.correct_lxml,
            name="override test value for name",
            base="override test value for base",
            maps=[
                Map(
                    unicode="override test value for unicode 1",
                    code="override test value for code 1",
                ),
                Map(
                    unicode="override test value for unicode 2",
                    code="override test value for code 2",
                ),
            ],
        )
        assert ude.base == "override test value for base"
        assert ude.name == "override test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "override test value for unicode 1"
        assert ude.maps[0].code == "override test value for code 1"
        assert ude.maps[1].unicode == "override test value for unicode 2"
        assert ude.maps[1].code == "override test value for code 2"
        assert isinstance(ude.maps[0], Map)
        assert isinstance(ude.maps[1], Map)
        assert isinstance(ude.maps, list)

        # Check ElementTree
        ude = Ude(
            self.correct_stdlib,
            name="override test value for name",
            base="override test value for base",
            maps=(
                Map(
                    unicode="override test value for unicode 1",
                    code="override test value for code 1",
                ),
                Map(
                    unicode="override test value for unicode 2",
                    code="override test value for code 2",
                ),
            ),
        )
        assert ude.base == "override test value for base"
        assert ude.name == "override test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "override test value for unicode 1"
        assert ude.maps[0].code == "override test value for code 1"
        assert ude.maps[1].unicode == "override test value for unicode 2"
        assert ude.maps[1].code == "override test value for code 2"
        assert isinstance(ude.maps[0], Map)
        assert isinstance(ude.maps[1], Map)
        assert isinstance(ude.maps, tuple)

    def test_create_ude_from_element_with_unknown_attribute(self):
        """
        Test that a Ude can be created from an xml element with an unknown
        attribute and that the unknown attribute is not in the Map's __dir__()
        Test both lxml and stdlib
        """
        # Check lxml
        ude = Ude(self.unknown_lxml)
        assert ude.base == "lxml test value for base"
        assert ude.name == "lxml test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "lxml test value for unicode 1"
        assert ude.maps[0].code == "lxml test value for code 1"
        assert ude.maps[1].unicode == "lxml test value for unicode 2"
        assert ude.maps[1].code == "lxml test value for code 2"
        assert "unknown" not in ude.__dir__()

        # Check ElementTree
        ude = Ude(self.unknown_stdlib)
        assert ude.base == "stdlib test value for base"
        assert ude.name == "stdlib test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "stdlib test value for unicode 1"
        assert ude.maps[0].code == "stdlib test value for code 1"
        assert ude.maps[1].unicode == "stdlib test value for unicode 2"
        assert ude.maps[1].code == "stdlib test value for code 2"
        assert "unknown" not in ude.__dir__()

    def test_create_ude_with_non_string_attribute_value(self):
        """
        Test that a Ude cannot be created using a non-string attribute values
        """
        ude = Ude(
            name=1,
            base=[1, 2, 3],
            maps=123.456,
        )
        assert ude.name == 1
        assert ude.base == [1, 2, 3]
        assert ude.maps == 123.456

    # ==========================================================================
    # Test the export of a Ude
    # ==========================================================================
    def test_export_ude(self):
        """
        Test that a Ude can be exported
        """
        ude = Ude(
            name="test value for name",
            base="value for base",
            maps=[],
        )
        elem = ude.to_element()
        assert elem.tag == "ude"
        assert elem.attrib["name"] == "test value for name"
        assert elem.attrib["base"] == "value for base"
        assert len(elem) == 0

    def test_export_ude_without_required_attributes(self):
        """
        Test that a Ude cannot be exported if it is missing required attributes
        """
        ude = Ude()
        with pytest.raises(AttributeError):
            ude.to_element()

    # test different map iterables
    def test_export_ude_with_list(self):
        """
        Test that a Ude can be exported with a list of maps
        """
        ude = Ude(
            name="test value for name",
            base="value for base",
            maps=[
                Map(
                    unicode="test value for unicode 1",
                    code="test value for code 1",
                    ent="test value for ent 1",
                ),
                Map(
                    unicode="test value for unicode 2",
                    code="test value for code 2",
                    ent="test value for ent 2",
                ),
            ],
        )
        list_elem = ude.to_element()
        assert list_elem.tag == "ude"
        assert list_elem.attrib["name"] == "test value for name"
        assert list_elem.attrib["base"] == "value for base"
        assert len(list_elem) == 2
        assert list_elem[0].tag == "map"
        assert list_elem[0].attrib["unicode"] == "test value for unicode 1"
        assert list_elem[0].attrib["code"] == "test value for code 1"
        assert list_elem[0].attrib["ent"] == "test value for ent 1"
        assert list_elem[0].tag == "map"
        assert list_elem[1].attrib["unicode"] == "test value for unicode 2"
        assert list_elem[1].attrib["code"] == "test value for code 2"
        assert list_elem[1].attrib["ent"] == "test value for ent 2"
        assert list_elem[1].tag == "map"

        def test_export_ude_with_tuple(self):
            """
            Test that a Ude can be exported with a tuple of maps
            """
            ude = Ude(
                name="test value for name",
                base="value for base",
                maps=(
                    Map(
                        unicode="test value for unicode 1",
                        code="test value for code 1",
                        ent="test value for ent 1",
                    ),
                    Map(
                        unicode="test value for unicode 2",
                        code="test value for code 2",
                        ent="test value for ent 2",
                    ),
                ),
            )
            tuple_elem = ude.to_element()
            assert tuple_elem.tag == "ude"
            assert tuple_elem.attrib["name"] == "test value for name"
            assert tuple_elem.attrib["base"] == "value for base"
            assert len(tuple_elem) == 2
            assert tuple_elem[0].tag == "map"
            assert tuple_elem[0].attrib["unicode"] == "test value for unicode 1"
            assert tuple_elem[0].attrib["code"] == "test value for code 1"
            assert tuple_elem[0].attrib["ent"] == "test value for ent 1"
            assert tuple_elem[0].tag == "map"
            assert tuple_elem[1].attrib["unicode"] == "test value for unicode 2"
            assert tuple_elem[1].attrib["code"] == "test value for code 2"
            assert tuple_elem[1].attrib["ent"] == "test value for ent 2"
            assert tuple_elem[1].tag == "map"

        def test_export_ude_with_set(self):
            """
            Test that a Ude can be exported with a set of maps
            """
            ude.maps = {
                Map(
                    unicode="test value for unicode",
                    code="test value for code",
                    ent="test value for ent",
                ),
                Map(
                    unicode="test value for unicode",
                    code="test value for code",
                    ent="test value for ent",
                ),
            }
            set_elem = ude.to_element()
            assert set_elem.tag == "ude"
            assert set_elem.attrib["name"] == "test value for name"
            assert set_elem.attrib["base"] == "value for base"
            assert len(set_elem) == 2
            assert set_elem[0].tag == "map"
            assert set_elem[0].attrib["unicode"] == "test value for unicode"
            assert set_elem[0].attrib["code"] == "test value for code"
            assert set_elem[0].attrib["ent"] == "test value for ent"
            assert set_elem[1].tag == "map"
            assert set_elem[1].attrib["unicode"] == "test value for unicode"
            assert set_elem[1].attrib["code"] == "test value for code"
            assert set_elem[1].attrib["ent"] == "test value for ent"
            assert set_elem[1].tag == "map"

            def test_export_ude_with_generator(self):
                """
                Test that a Ude can be exported with a generator of maps
                """
                ude.maps = (
                    Map(
                        unicode=f"test value for unicode {x}",
                        code=f"test value for code {x}",
                        ent=f"test value for ent {x}",
                    )
                    for x in range(2)
                )
                gen_elem = ude.to_element()
                assert gen_elem.tag == "ude"
                assert gen_elem.attrib["name"] == "test value for name"
                assert gen_elem.attrib["base"] == "value for base"
                assert len(gen_elem) == 2
                assert gen_elem[0].tag == "map"
                assert gen_elem[0].attrib["unicode"] == "test value for unicode 0"
                assert gen_elem[0].attrib["code"] == "test value for code 0"
                assert gen_elem[0].attrib["ent"] == "test value for ent 0"
                assert gen_elem[1].tag == "map"
                assert gen_elem[1].attrib["unicode"] == "test value for unicode 1"
                assert gen_elem[1].attrib["code"] == "test value for code 1"
                assert gen_elem[1].attrib["ent"] == "test value for ent 1"
                assert gen_elem[1].tag == "map"

        def test_export_ude_with_dict_values(self):
            """
            Test that a Ude can be exported with a view of dict values of maps
            """
            ude.maps = {
                "Map1": Map(
                    unicode="test value for unicode 1",
                    code="test value for code 1",
                    ent="test value for ent 1",
                ),
                "Map2": Map(
                    unicode="test value for unicode 2",
                    code="test value for code 2",
                    ent="test value for ent 2",
                ),
            }.values()
            dict_elem = ude.to_element()
            assert dict_elem.tag == "ude"
            assert dict_elem.attrib["name"] == "test value for name"
            assert dict_elem.attrib["base"] == "value for base"
            assert len(dict_elem) == 2
            assert dict_elem[0].tag == "map"
            assert dict_elem[0].attrib["unicode"] == "test value for unicode 1"
            assert dict_elem[0].attrib["code"] == "test value for code 1"
            assert dict_elem[0].attrib["ent"] == "test value for ent 1"
            assert dict_elem[0].tag == "map"
            assert dict_elem[1].attrib["unicode"] == "test value for unicode 2"
            assert dict_elem[1].attrib["code"] == "test value for code 2"
            assert dict_elem[1].attrib["ent"] == "test value for ent 2"
            assert dict_elem[1].tag == "map"

    def test_export_ude_with_no_base_when_required(self):
        """
        Test that a Ude cannot be exported without a base if at least one
        of it Map elements has a code attribute.
        """
        ude = Ude(
            name="test value for name",
            maps=[Map(unicode="test value for unicode", code="test value for code")],
        )
        with pytest.raises(AttributeError):
            ude.to_element()

    def test_export_with_incorrect_attribute_value(self):
        """
        Test that a Ude cannot be exported with incorrect attribute values.
        """
        ude = Ude(
            name="test value for name",
            maps=Map(unicode="test value for unicode"),
        )
        with pytest.raises(TypeError):
            ude.to_element()
        ude.name = 1
        with pytest.raises(TypeError):
            ude.to_element()
