from os import PathLike
from pathlib import Path
from warnings import warn

from lxml.etree import ElementTree

from PythonTmx.structural import Tmx


def from_file(path: PathLike, strict: bool = False) -> Tmx:
  path = Path(path)
  if not path.exists():
    raise FileNotFoundError(f"File '{path}' does not exist")
  if not path.is_file():
    raise IsADirectoryError(f"File '{path}' is not a file")
  if not path.suffix == ".tmx":
    warn("File is not a .tmx file")
  with path.open("r", encoding="utf-8") as fp:
    return Tmx(elem=ElementTree(file=fp).getroot(), strict=strict)
