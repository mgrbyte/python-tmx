.. toctree::
   :hidden:

   Classes <PythonTmx.classes>
   Utils <PythonTmx.utils>


PythonTmx
=========

PythonTmx is a Python library for manipulating, creating, and editing
Translation Memory eXchange (TMX) files built on topp of the lxml library.

The main aim of this library is to provide a simple and intuitive API to work
with TMX files by abstratcting away the complexity of the XML format and the 
potential for errors of working with strings and xml elements directly.

Features
--------

- **Read TMX Files**: Load and parse existing TMX files to access translation memory data.
- **Create TMX Files**: Generate new TMX files from scratch.
- **Edit TMX Files**: Modify existing TMX files by adding, removing, or updating translation units.
- **Datetime Support**: Use Python Datetime objects to represent dates and times instead of strings.
- **Fully Typed**: PythonTmx is fully typed, providing type hints and type checking for all attributes and methods.
- **Fully Tmx 1.4 level 2 compliant**: PythonTmx supports all the elements and attributes of TMX 1.4 level 2, letting you build and parse even the most complex files
- **Built on top of lxml**: PythonTmx uses the lxml library to parse and generate XML by default.

.. note::
   
   While PythonTmx is built on top of, and is meant to be used with lxml, it is
   fully compatible AND typed for use with Python's built-in xml.etree.ElementTree
   module. Simply set `lxml` to False when using `to_element` and `from_element`
   to use the native ElementTree module instead.

Installation
------------

You can install PythonTmx using pip:

.. code-block:: sh

    pip install python-tmx

Usage
-----

Here is a basic example of how to use PythonTmx.

.. code-block:: python

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

API Reference
-------------
- `Classes <PythonTmx.classes>`_
- `Utils <PythonTmx.utils>`_

License
-------

PythonTmx is licensed under the MIT License. See the `LICENSE <https://github.com/EnzoAgosta/python-tmx/blob/main/LICENSE>`_ file for more details.
