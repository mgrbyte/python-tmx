PythonTmx
=========

PythonTmx is a python library meant to make manipulating Translation
Memory Exchange (TMX) files easier and more pythonic.

Installation
------------

Install from pip

.. code:: bash

     pip install python-tmx

Documentation
-------------
.. :toctree::
    :depth: 4
    
`Structural Elements <PythonTmx.structural.html>`_

`Inline Elements <PythonTmx.inline.html>`_

`Utils <PythonTmx.utils.html>`_
   
Usage/Examples
--------------

Using PythonTmx is as simple as feeding a lxml Element to its
corresponding constructor and treating as normal python object or
creating one from scratch to convert anything into a valid tmx file.

Every element in the library can be instantiated using the `elem` attribute.
It is meant to receive an lxml Element, but is fully compatible with the stdlib
ElementTree library. If for some reason you want to use another xml library
to read tmx files, simply make sure that the object you pass to the constructor
adheres to the ``XmlElementLike`` Protocol.

It also possible to provide values for any other attributes along with ``elem``.
When a constructor receives both ``elem`` and a keyword argument. That attribute
will not be parsed and the provided value will be used instead.

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
