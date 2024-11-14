import xml.etree.ElementTree as stdET

import lxml.etree as lxmlET
import pytest

from PythonTmx.structural import Map, Ude


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

    def test_create_ude_from_element(self):
        """
        Test that a Ude can be created from an xml element
        Test both lxml and stdlib
        """
        # Check lxml
        ude = Ude(
            lxmlET.fromstring(
                """<ude name="lmxl test value for name" base="lmxl test value for base">
            <map unicode="lmxl test value for unicode 1" code="lmxl test value for code 1"/>
            <map unicode="lmxl test value for unicode 2" code="lmxl test value for code 2"/>
            </ude>"""
            )
        )
        assert ude.base == "lmxl test value for base"
        assert ude.name == "lmxl test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "lmxl test value for unicode 1"
        assert ude.maps[0].code == "lmxl test value for code 1"
        assert ude.maps[1].unicode == "lmxl test value for unicode 2"
        assert ude.maps[1].code == "lmxl test value for code 2"

        # Check ElementTree
        ude = Ude(
            stdET.fromstring(
                """<ude name="stdlib test value for name" base="stdlib test value for base">
            <map unicode="stdlib test value for unicode 1" code="stdlib test value for code 1"/>
            <map unicode="stdlib test value for unicode 2" code="stdlib test value for code 2"/>
            </ude>"""
            )
        )
        assert ude.base == "stdlib test value for base"
        assert ude.name == "stdlib test value for name"
        assert len(ude.maps) == 2
        assert ude.maps[0].unicode == "stdlib test value for unicode 1"
        assert ude.maps[0].code == "stdlib test value for code 1"
        assert ude.maps[1].unicode == "stdlib test value for unicode 2"
        assert ude.maps[1].code == "stdlib test value for code 2"

    def test_create_ude_from_incorrect_element(self):
        """
        Test that a Ude cannot be created from an incorrect xml element
        Test both lxml and stdlib
        """
        # Check lxml
        with pytest.raises(ValueError):
            Ude(lxmlET.fromstring("<wrongtag/>"))

        # Check ElementTree
        with pytest.raises(ValueError):
            Ude(stdET.fromstring("<wrongtag/>"))

    def test_create_ude_from_element_override_values(self):
        """
        Test that a Ude can be created from an xml element with keyword
        arguments
        Test both lxml and stdlib
        """
        # Check lxml
        ude = Ude(
            lxmlET.fromstring(
                """<ude name="lmxl test value for name" base="lmxl test value for base">
            <map unicode="lmxl test value for unicode 1" code="lmxl test value for code 1"/>
            <map unicode="lmxl test value for unicode 2" code="lmxl test value for code 2"/>
            </ude>"""
            ),
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
            stdET.fromstring(
                """<ude name="stdlib test value for name" base="stdlib test value for base">
            <map unicode="stdlib test value for unicode 1" code="stdlib test value for code 1"/>
            <map unicode="stdlib test value for unicode 2" code="stdlib test value for code 2"/>
            </ude>"""
            ),
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
