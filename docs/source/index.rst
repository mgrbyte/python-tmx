.. toctree:: PythonTmx.structural
    :maxdepth: 4
    :hidden:

.. toctree:: PythonTmx.inline
    :maxdepth: 4
    :hidden:
    
.. toctree:: PythonTmx.utils
    :maxdepth: 4
    :hidden:

PythonTmx
=========

PythonTmx is a python library meant to make manipulating Translation
Memory Exchange (TMX) files easier and more pythonic.

Installation
------------

Install from pip

.. code:: bash

     pip install python-tmx


Description
-----------

The main philosophy behind PythonTmx is to let `you` do whatever you want easier
rather than be a one stop shop for tmx file utility functions. While I might add
some useful ones to the ``utils`` module later down the line. The main priority
is to add an abstraction layer when dealing with TMX files that deals with type
checking, attributes and ensuring tmx files are valid for you, letting you do
what you want without having to deal with the raw xml output of lxml.

Using PythonTmx is as simple as parsing a tmx file using lxml or ElementTree
and feeding the resulting element to the ``Tmx`` constructor. Note that `every`
class also support being created from a xml Element. So if you simply want to
interact with the header and not touch the tus, you can also parse only
that element from the file, feed it to the ``Header`` constructor, do what you
need to do, export that ``Header`` back to an element, replace the one in the
file with yours, and be done with it.

While the library is created with lxml in mind, it is also fully compatible
with the stdlib ElementTree library with `no codes change required`.
If for some reason you want to use another xml library to read tmx files,
simply make sure that the object you pass to the constructor adheres to
the ``XmlElementLike`` Protocol before feeding your element to PythonTmx.

It also possible to provide values for any other attributes along with ``elem``.
When a constructor receives both ``elem`` and a keyword argument. That attribute
will not be parsed and the provided value will be used instead.

From there, you can manipulate it however you want, grabbing any attribute from
an object using dot notation, e.g. to get ``lang`` attribute from a
``Note`` object called ``my_note`` simply do ``my_note.lang``.

Examples
--------

Making a tmx file bilngual
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   from datetime import UTC, datetime

   from lxml.etree import ElementTree, parse

   from PythonTmx.structural import Tmx

   # tmx files are valid xml so use lxml to parse them
   root = parse("Translation Memory.tmx").getroot()

   # convert to a Tmx Object by simply feeding the element to the constructor
   tmx_obj = Tmx(elem=root)

   # iterate over all tu and their tuv
   for tu in tmx_obj.tus:
       for tuv in tu.tuvs:
           # remove any tuv that's not english or german
           if tuv.lang not in ("en", "de"):
               tu.pop(tuv)
   # update the changedate in the header
   tmx_obj.header.changedate = datetime.now(UTC)

   # export the tmx back to an lxml ELement and use lxml to export it to a file again
   new_root = tmx_obj.to_element()
   ElementTree(new_root).write("Bilingual.tmx")

Converting a csv to a Tmx file from scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   import csv
   import PythonTmx.structural as tm
   from lxml.etree import parse, ElementTree
   from datetime import datetime, UTC


   # create a header with all the relevant info
   my_header = tm.Header(
       creationtool="PythonTmx",
       creationtoolversion="0.3",
       datatype="PlainText",
       segtype="sentence",
       adminlang="en-us",
       srclang="EN",
       tmf="csv",
       creationdate=datetime.now(UTC),
       creationid="Enzo Agosta",
       changeid="Enzo Agosta",
   )
   # create an empty Tmx object with our header
   tmx = tm.Tmx(header=my_header)

   with open("translations.csv", encoding="utf-8") as file:
       #read the csv and start iterating
       lines = csv.reader(file)
       for line in lines:
           # create a Tuv/language
           english = tm.Tuv(
               segment=line[0],
               lang="en",
               creationtool=my_header.creationtool,
               creationtoolversion=my_header.creationtool,
               creationdate=datetime.now(UTC),
               tmf=my_header.tmf,
           )
           german = tm.Tuv(
               segment=line[1],
               lang="de",
               creationtool=my_header.creationtool,
               creationtoolversion=my_header.creationtool,
               creationdate=datetime.now(UTC),
               tmf=my_header.tmf,
           )
           spanish = tm.Tuv(
               segment=line[2],
               lang="es",
               creationtool=my_header.creationtool,
               creationtoolversion=my_header.creationtool,
               creationdate=datetime.now(UTC),
               tmf=my_header.tmf,
           )
           # Append the Tuv to main Tmx object
           tmx.tus.append(
               tm.Tu(
                   tuvs=[english, german, spanish],
                   creationtool=my_header.creationtool,
                   creationtoolversion=my_header.creationtool,
                   creationdate=datetime.now(UTC),
                   tmf=my_header.tmf,
                   srclang="en",
               )
           )
   # export the tmx back to an lxml ELement and use lxml to export it to a file again
   new_root = tmx_obj.to_element()
   ElementTree(new_root).write("From csv.tmx")

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`__

.. |MIT License| image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: https://choosealicense.com/licenses/mit/
.. |Python Version from PEP 621 TOML| image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FChonkyYoshi%2Fpython-tmx%2Frefs%2Fheads%2Fmain%2Fpyproject.toml
