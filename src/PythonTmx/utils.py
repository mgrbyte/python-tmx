from csv import reader, writer
from datetime import UTC, datetime
from os import PathLike
from pathlib import Path

from lxml.etree import ElementTree, XMLParser, fromstring, parse, tostring

from PythonTmx.inline import _parse_inline
from PythonTmx.structural import Header, Tmx, Tu, Tuv


def from_file(file: PathLike, *, encoding: str = "utf-8", strict: bool = True) -> Tmx:
    """
    Parses a tmx file and create a :class:`Tmx` object from it

    Parameters
    ----------
    file : PathLike
        The path to the tmx file to process. Can be a str, bytes, a file
        object from ``open()`` a ``Path`` Object.
    encoding : str, optional
        The encoding to use when reading the files, by default "utf-8"
    strict : bool, optional
        True to error if the file extension is not ".tmx", by default True

    Returns
    -------
    Tmx
        A :class:`Tmx` object

    Raises
    ------
    ValueError
        If a path doesn't exists, is a folder, or is not a ".tmx" file if
        ``strict`` is turned on.
    """
    f: Path = Path(file)
    if not f.exists():
        raise ValueError(f"{f.absolute()} is not a valid path")
    if not f.is_file():
        raise ValueError(f"{f.resolve()} is a folder not a file")
    if f.suffix != ".tmx" and strict:
        raise ValueError(f"{f.resolve()} is not a tmx file")
    root_elem = parse(
        source=f, parser=XMLParser(encoding=encoding, resolve_entities=True)
    ).getroot()
    return Tmx(elem=root_elem)


def to_file(tmx: Tmx, file: PathLike, *, encoding: str = "utf-8") -> None:
    """
    Writes a :class:`Tmx` object to a file

    Parameters
    ----------
    tmx : Tmx
        The :class:`Tmx` object to write
    file : PathLike
        The file to write to
    encoding : str, optional
        The encoding to use, by default "utf-8"
    """
    f: Path = Path(file)
    ElementTree(tmx.to_element()).write(f, encoding, xml_declaration=True)


def from_csv(
    file: PathLike,
    src_col: int,
    src_lang: str,
    trg_col: int,
    trg_lang: str,
    *,
    skip_header_line: bool = True,
    encoding: str = "utf-8",
    strict: bool = True,
    tmx_header: Header | None = None,
) -> Tmx:
    """
    Parses a csv file and create a :class:`Tmx` object from it

    Parameters
    ----------
    file : PathLike
        The path to the tmx file to process. Can be a str, bytes, a file
        object from ``open()`` a ``Path`` Object.
    src_col : int
        The source column number
    src_lang : str
        The source language, will be used for all :class:`Tu` and the
        :class:`Header` if no header is provided.
    trg_col : int
        The target column number
    trg_lang : str
        The target language, will be used for all :class:`Tu`.
    skip_header_line : bool, optional
        Whetehr the first line in the csv should be skipped, by default True
    encoding : str, optional
        The encoding to use when reading the files, by default "utf-8"
    strict : bool, optional
        True to error if the file extension is not ".tmx", by default True
    tmx_header : Header | None, optional
        A header to use for the resulting tmx file, a default header will be
        created if None, by default None

    Returns
    -------
    Tmx
        A Tmx file, with optionally the header provided and all the tus parsed.

    Raises
    ------
    ValueError
        If a path doesn't exists, is a folder, or is not a ".csv" file if
        ``strict`` is turned on.
    """
    f: Path = Path(file)
    if not f.exists():
        raise ValueError(f"{f.absolute()} is not a valid path")
    if not f.is_file():
        raise ValueError(f"{f.resolve()} is a folder not a file")
    if f.suffix != ".csv" and strict:
        raise ValueError(f"{f.resolve()} is not a csv file")
    with open(file=f, encoding=encoding) as fp:
        lines = reader(fp)
        if skip_header_line:
            _ = next(lines)
        _tus: list[Tu] = [
            Tu(
                tuvs=[
                    Tuv(
                        segment=_parse_inline(
                            fromstring(f"<seg>{line[src_col]}</seg>")
                        ),
                        lang=src_lang,
                    ),
                    Tuv(
                        segment=_parse_inline(
                            fromstring(f"<seg>{line[trg_col]}</seg>")
                        ),
                        lang=trg_lang,
                    ),
                ]
            )
            for line in lines
        ]
    return Tmx(
        header=(
            tmx_header
            if tmx_header is not None
            else Header(
                creationtool="PythonTmx",
                creationtoolversion="0.3",
                segtype="sentence",
                tmf="csv",
                adminlang="en",
                srclang=src_lang,
                creationdate=datetime.now(UTC),
            )
        ),
        tus=_tus,
    )


def to_csv(tmx: Tmx, file: PathLike, *, encoding: str = "utf-8") -> None:
    """
    Writes a :class:`Tmx` object to a csv file

    Parameters
    ----------
    tmx : Tmx
        The :class:`Tmx` object to write
    file : PathLike
        The file to write to
    encoding : str, optional
        The encoding to use, by default "utf-8"
    """
    f = Path(file)
    with open(f, "w", encoding=encoding) as fp:
        csv_file = writer(fp, lineterminator="\n")
        for tu in tmx.tus:
            csv_file.writerow(
                [
                    tostring(tuv.to_element().find("seg"), encoding="unicode")[5:-6]
                    for tuv in tu.tuvs
                ]
            )


to_csv(from_csv("a.csv", 1, "en", 2, "es"), "b.csv")
