from unittest import TestCase

from lxml.etree import fromstring

from PythonTmx.structural import Header, Tmx, Tu, Tuv


class TestTmx(TestCase):
  def test_create_export_empty_tu(self):
    tmx = Tmx()
    self.assertIsInstance(tmx.header, Header)
    self.assertEqual(tmx.tus, [])
    with self.assertRaises(AttributeError):
      tmx.to_element()

  def test_create_tmx_from_element(self):
    elem = fromstring(
      """<tmx version="1.4">
                <header creationtool="PythonTmx" creationtoolversion="0.3" 
            datatype="PlainText" segtype="sentence" adminlang="en-us"
            srclang="en-US" o-tmf="xml string" creationdate="20241119T162345Z"
            creationid="Enzo" changedate="20241120T155800Z" changeid="DJ Khaled"
            o-encoding="utf-8">
                <prop type="x-tmx-header-comment">This is a comment</prop>
                <note>This is a note</note>
                <ude name="ude name" base="ude base">
                    <map unicode="unicode" code="code" ent="ent" subst="subst"/>
                </ude>
            </header>
            <body>
            <tu tuid="coolid"
                o-encoding="utf-8"
                datatype="Plaintext"
                usagecount="12"
                lastusagedate="20241120T120000Z"
                creationtool="PythonTmx Test Suite"
                creationtoolversion="0.3"
                creationdate="20221120T120000Z"
                creationid="PythonTmx"
                changedate="20241120T120000Z"
                segtype="sentence"
                changeid="Testing"
                o-tmf="testing"
                srclang="en-us">
              <tuv xml:lang="en-US">
                <seg>Potatoes</seg>
              </tuv>
              <prop type="Domain">Cooking</prop>
              <tuv xml:lang="fr-CA">
                <seg>Pomme de terre</seg>
              </tuv>
              <tuv xml:lang="de-DE">
                <seg>Kartoffel</seg>
              </tuv>
              <note>This is a note</note>
              </tu>
              </body>
              </tmx>
              """
    )
    tmx = Tmx(elem)
    self.assertIsInstance(tmx.header, Header)
    self.assertIsInstance(tmx.tus, list)
    self.assertEqual(len(tmx.tus), 1)
    self.assertIsInstance(tmx.tus[0], Tu)

  def test_export_minimal_tmx(self):
    tmx = Tmx(
      tus=[Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")])],
      header=Header(
        creationtool="creationtool",
        creationtoolversion="1.0",
        segtype="sentence",
        tmf="tmf",
        adminlang="en-us",
        srclang="en-US",
        datatype="PlainText",
        encoding="utf-8",
      ),
    )
    elem = tmx.to_element()
    self.assertEqual(
      elem.tag,
      "tmx",
    )
    self.assertEqual(elem.get("version"), "1.4")
    self.assertEqual(len(elem), 2)
    body = elem.find("body")
    self.assertEqual(len(body.findall("tu")), len(tmx.tus))
    self.assertEqual(len(body.find("tu").findall("tuv")), len(tmx.tus[0].tuvs))

  def test_add_unknown_attributes(self):
    tmx = Tmx()
    with self.assertRaises(AttributeError):
      tmx.other = "test"

  def test_create_tmx_from_element_with_unknwon_attributes(self):
    elem = fromstring("""<tmx other="other">
                <header creationtool="creationtool" />
                <body>
                </body>
              </tmx>""")
    new_tmx = Tmx(elem)
    self.assertNotIn("other", new_tmx.__dir__())
    self.assertEqual(new_tmx._source_elem, elem)

  def test_create_tu_from_element_with_kwargs(self):
    elem = fromstring(
      """<tmx>
                <header creationtool="creationtool" />
                <body>
                </body>
              </tmx>
            """
    )
    tmx = Tmx(elem, header=Header(creationtool="override creationtool"))
    self.assertEqual(tmx._source_elem, elem)
    self.assertEqual(tmx.header.creationtool, "override creationtool")

  def test_use_tmx_dunder_methods(self):
    tmx = Tmx()
    tmx.header = "header"
    self.assertEqual(tmx.header, tmx["header"])
    tmx["header"] = "new header"
    self.assertEqual(tmx["header"], "new header")
    with self.assertRaises(KeyError):
      tmx["unknown"]
    with self.assertRaises(KeyError):
      tmx["unknown"] = "test"
    del tmx["header"]
    self.assertIsNone(tmx.header)
    tmx.tus = [Tu() for x in range(10)]
    for i in tmx.tus:
      self.assertIsInstance(i, Tu)

  def test_create_tmx_from_element_wrong_tag(self):
    with self.assertRaises(ValueError):
      Tmx(fromstring("<wrong_tag/>"))

  def test_export_tmx_wrong_attribute_type(self):
    tmx = Tmx(
      header=Header(
        creationtool="creationtool",
        creationtoolversion="1.0",
        segtype="sentence",
        tmf="tmf",
        adminlang="en-us",
        srclang="en-US",
        datatype="PlainText",
        encoding="utf-8",
      )
    )
    tmx.tus = 123
    with self.assertRaises(TypeError):
      tmx.to_element()

  def test_export_tmx_any_iterable(self):
    tmx = Tmx(
      header=Header(
        creationtool="creationtool",
        creationtoolversion="1.0",
        segtype="sentence",
        tmf="tmf",
        adminlang="en-us",
        srclang="en-US",
        datatype="PlainText",
        encoding="utf-8",
      )
    )

    # list
    tmx.tus = [Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")])]
    elem = tmx.to_element()
    body = elem.find("body")
    self.assertEqual(len(body.findall("tu")), 1)
    # tuple
    tmx.tus = (Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")]),)
    elem = tmx.to_element()
    body = elem.find("body")
    self.assertEqual(len(body.findall("tu")), 1)
    # set
    tmx.tus = {Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")])}
    elem = tmx.to_element()
    body = elem.find("body")
    self.assertEqual(len(body.findall("tu")), 1)

    # Dict Value
    tmx.tus = {1: Tu(tuvs=[Tuv(segment="Potatoes", lang="en-US")])}.values()
    elem = tmx.to_element()
    body = elem.find("body")
    self.assertEqual(len(body.findall("tu")), 1)
