from datetime import datetime
from json import dump
from os import PathLike

from lxml.etree import ElementTree, _Element, parse

from .core import Tmx, TmxElement
from .errors import IncorrectRootError
from .export import tmx_to_element
from .parse import parse_tmx

__all__ = [
    "load_tmx",
    "to_tmx_file",
    "to_json",
]


def load_tmx(file: str | bytes | PathLike) -> Tmx:
    root: _Element = parse(file).getroot()
    if root.tag != "tmx":
        raise IncorrectRootError()
    return parse_tmx(root)


def to_tmx_file(
    tmx: Tmx, file: str | bytes | PathLike, encoding: str = "UTF-8"
) -> None:
    root = tmx_to_element(tmx)
    ElementTree(root).write(
        file,
        encoding=encoding.upper(),
        xml_declaration=True,
        doctype='<!DOCTYPE tmx SYSTEM "tmx14.dtd">',
    )


def to_json(
    element: TmxElement, file: str | bytes | PathLike, encoding: str = "utf-8"
) -> None:
    def default(obj) -> dict[str, str]:
        if isinstance(obj, datetime):
            return obj.strftime(r"%Y%m%dT%H%M%SZ")
        else:
            return obj.__dict__

    with open(file, "w", encoding=encoding) as f:
        dump(element, f, ensure_ascii=False, indent=2, default=default)
