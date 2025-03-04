.. toctree:: PythonTmx.classes
   :maxdepth: 4
   :hidden:

.. toctree:: PythonTmx.utils
   :maxdepth: 4
   :hidden:

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
- **Blazing Fast**: Leverage the power of the lxml library for efficient XML parsing and manipulation.
- **Datetime Support**: Use Python Datetime objects to represent dates and times instead of strings.
- **Fully Typed**: PythonTmx is fully typed, providing type hints and type checking for all attributes and methods.
- **Fully Tmx 1.4 level 2 support**: PythonTmx supports all the elements and attributes of TMX 1.4 level 2, letting you build and parse even the most complex files

Installation
------------

You can install PythonTmx using pip:

.. code-block:: sh

    pip install python-tmx

Usage
-----

Here is a basic example of how to use PythonTmx to load and read a TMX file:

.. code-block:: python

      import PythonTmx as tmx
      from datetime import datetime, UTC

      # Load a TMX file
      tmx_file = tmx.from_file("path/to/translation_memory.tmx")

      # Add notes to the header
      tmx_file.header.notes.append(tmx.Note(text="This is a note", lang="en"))
      tmx_file.header.notes.append(tmx.Note(text="Este es un nota", lang="es"))

      # Find incomplete translation units
      incomplete_tus = [tu for tu in tmx_file.tus if len(tu.tuvs) < 2]

      # Add a new translation unit
      tu = tmx.Tu(tuid="mytuid", creationdate=datetime.now(UTC))
      tu.tuvs.append(
      tmx.Tuv(
         lang="en",
         content=["Hello ", tmx.Ph(content=["Hi this is a placeholder"], i=1), "world!"],
      )
      )
      tu.tuvs.append(
      tmx.Tuv(
         lang="es",
         content=["Hola ", tmx.Ph(content=["Hi this is a placeholder"], i=1), "mundo!"],
      )
      )
      tmx_file.tus.append(tu)

      # Save the modified TMX file
      tmx.to_file(tmx_file, "path/to/translation_memory.tmx")


For more detailed usage and examples, please refer to the documentation.

Documentation
-------------

The full documentation for PythonTmx is available at the following link:

`PythonTmx Documentation <https://github.com/ChonkyYoshi/python-tmx>`_

License
-------

PythonTmx is licensed under the MIT License. See the LICENSE file for more details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`