Intro
=====

At its core, PythonTmx is meant to be a simple wrapper around the lxml library
to make working with TMX files easier and more pythonic.

Every element from the TMX 1.4 specification is represented by a class in
PythonTmx. Each class's attributes are modeled after the attributes of the
corresponding element in the TMX specification. For example, the `Bpt` class
has an `i` attribute that corresponds to the `i` attribute of the `bpt` element
in the TMX specification.

While PythonTmx is meant to be used by developpers who are already familiar with
the TMX specification, this intro will provide a brief overview of how TMX files
are structured and how to work with them using PythonTmx for complete beginners.

Basics
------

Tmx files are a flavor of XML files that follow a specific structure. The
structure of a TMX file is defined in the `TMX 1.4 specification <https://www.gala-global.org/sites/default/files/tmx14.dtd>`_.

Elements are divided into two main categories: inline elements and structural
elements. Structural elements are the ones that contain other elements, such as
`Header`, `Tu`, `Tuv`, etc and act as the building blocks of the TMX file.

Inline elements are the ones that contain the actual content of the TMX file.
They contain text and can be nested infinitely.

A Tmx file contains only 1 root element, which is the `tmx` element. This
element contains the `header` element, which contains information about the
TMX file, such as the creation date, the creation tool, etc. It also contains
any number of `tu` elements, which contain the actual translation units.

Structural elements can contain `note` and `prop` elements, which contain
additional information about the element. For example, a `note` element can
contain a note about context regarding a translation unit, or the file itself, 
or a `prop` element can contain a custom property that can be used to store
information about the translation unit to be used later by another tool.

Tmx files also support custom, user-defined encodings using the `ude` and `map`
elements. These elements allow you to define custom encodings that can be used
to represent text in a specific way.

.. note::

    While PythonTmx supports parsing, editing and exporting `ude` and `map`
    elements, it does NOT use those in any way at this time and are simply
    here for compatibility with the TMX specification.


Structure
---------

The structure of a TMX file is as follows:

.. code-block:: xml

    <tmx version="1.4">
        <header>
            <note>...</note>
            ...
            <prop>...</prop>
            ...
            <ude>
              <map />
              ...
            </ude>
        </header>
        <body>
          <tu>
              <tuv>
                  <note>...</note>
                  ...
                  <prop>...</prop>
                  ...
                  <seg>...</seg>
              </tuv>
          </tu>
          ...
        </body>
    </tmx>