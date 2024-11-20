from typing import TypeAlias
from xml.etree.ElementTree import Element

from lxml.etree import _Element

XmlElementLike: TypeAlias = _Element | Element
