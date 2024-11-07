from datetime import datetime
from typing import Any, SupportsInt

from lxml.etree import _Element

_xml_ = r"{http://www.w3.org/XML/1998/namespace}"


def add_attrs(
    elem: _Element, attrs: dict[str, Any], req: tuple[str, ...], force_str: bool = False
) -> None:
    """
    Please???????????????????????????????????????????????????????????????????????????????
    """
    for key, val in attrs.items():
        if val is None:
            if key in req:
                raise ValueError(
                    f"Attribute '{key}' is required and cannot have a value of None when used on a {elem.tag.capitalize()} Element"
                )
            continue
        if key in (
            "adminlang",
            "base",
            "changeid",
            "code",
            "creationid",
            "creationtool",
            "creationtoolversion",
            "datatype",
            "ent",
            "name",
            "srclang",
            "subst",
            "tuid",
            "type",
            "unicode",
        ):
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            elem.set(key, val)
        elif key == "lang":
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            elem.set(f"{_xml_}lang", str(val))
        elif key in ("tmf", "encoding"):
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            elem.set(f"o-{key}", val)
        elif key == "segtype":
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            if val.lower() not in ("block", "paragraph", "sentence", "phrase"):
                raise ValueError(
                    "the 'segtype' attribute must be one of "
                    "'block', 'paragraph', 'sentence', 'phrase'"
                    f"but got {key.lower()}"
                )
            elem.set(key, val.lower())
        elif key in ("creationdate", "changedate", "lastusagedate"):
            if isinstance(val, datetime):
                elem.set(key, val.strftime(r"%Y%m%dT%H%M%SZ"))
            else:
                if not isinstance(val, str):
                    if force_str:
                        val = str(val)
                    else:
                        raise TypeError(
                            f"Attribute '{key}' must be a string or datetime object when used on a '{elem.tag.capitalize()}' Element."
                        )
                try:
                    elem.set(
                        key,
                        datetime.strptime(val, r"%Y%m%dT%H%M%SZ").strftime(
                            r"%Y%m%dT%H%M%SZ"
                        ),
                    )
                except ValueError as e:
                    raise ValueError(
                        f"The '{key}' attribute must be formatted as YYYYMMDDTHHMMSSZ"
                    ) from e
        elif key in ("usagecount", "i", "x"):
            if isinstance(val, SupportsInt):
                elem.set(key, str(int(val)))
            else:
                if not isinstance(val, str):
                    if force_str:
                        val = str(val)
                    else:
                        raise TypeError(
                            f"Attribute '{key}' must be a string or convertible to an int when used on a '{elem.tag.capitalize()}' Element."
                        )
                elem.set(key, val)
        elif key == "pos":
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            if val.lower() not in (
                "begin",
                "end",
            ):
                raise ValueError(
                    "the 'segtype' attribute must be one of 'begin' or 'end'"
                    f"but got {key.lower()}"
                )
            elem.set(key, val.lower())
        elif key == "assoc":
            if not isinstance(val, str):
                if force_str:
                    val = str(val)
                else:
                    raise TypeError(
                        f"Attribute '{key}' must be a string when used on a '{elem.tag.capitalize()}' Element."
                    )
            if val.lower() not in (
                "p",
                "f",
                "b",
            ):
                raise ValueError(
                    "the 'segtype' attribute must be one of 'p','f' or 'b'"
                    f"but got {key.lower()}"
                )
            elem.set(key, val.lower())


def initialise_logger(output_file, mode) -> None:
    """
    Setup logging to console and file simultanenously. The process is described here:
    Logging to Console and File In Python

    :param output_file: log file to use. Frequently we set this to:
    .. highlight:: python
    .. code-block:: python

            logname = __file__.replace("./", "").replace(".py", "")
            os.path.join("logs", "{}.log".format(logname))

    :param mode: `both` or `file only` selects whether output is sent to file and console, or file only

    :return: No return value
    """
    ...
