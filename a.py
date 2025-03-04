from datetime import UTC, datetime

import lxml.etree as etree

import PythonTmx as tmx

# Load a TMX file
tmx_file: etree._ElementTree = etree.parse(
  "path/to/translation_memory.tmx", etree.XMLParser(encoding="utf-8")
)
tmx_root: etree._Element = tmx_file.getroot()
tmx_obj: tmx.TmxElement = tmx.from_element(tmx_root)

# Check if the TMX file is valid
assert isinstance(tmx_obj, tmx.Tmx), "The TMX file is not valid"

# Add notes and props to the header
tmx_obj.header.notes.append(tmx.Note(text="This is a note", lang="en"))
tmx_obj.header.notes.append(tmx.Note(text="Este es un nota", lang="es"))
tmx_obj.header.props.append(
  tmx.Prop(text="This is a prop", lang="en", type="x-my-prop")
)

# Remove incomplete translation units
tmx_obj.tus = [tu for tu in tmx_obj.tus if len(tu.tuvs) < 2]

# Add a new translation unit
tu = tmx.Tu(tuid="mytuid", creationdate=datetime.now(UTC))
tu.tuvs.append(
  tmx.Tuv(
    lang="en",
    content=[
      "Hello ",
      tmx.Ph(content=["Hi this is a placeholder"], x=1),
      "world!",
    ],
  )
)
tu.tuvs.append(
  tmx.Tuv(
    lang="es",
    content=[
      "Hola ",
      tmx.Ph(content=["Hi this is a placeholder"], x=1),
      "mundo!",
    ],
  )
)
tmx_obj.tus.append(tu)

# Edit the header to keep track of the changes
tmx_obj.header.changedate = datetime.now(UTC)
tmx_obj.header.changeid = "MyUser"

# Save and export the modified TMX file
new_tmx_root: etree._Element = tmx.to_element(tmx_obj)
etree.ElementTree(new_tmx_root).write(
  "path/to/translation_memory.tmx", encoding="utf-8", xml_declaration=True
)
