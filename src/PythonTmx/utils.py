from datetime import datetime
from typing import Any

from PythonTmx import XmlElementLike


def _parse_int_attr(
    elem: XmlElementLike | None, attr: str, value: Any | None
) -> int | Any | None:
    if value is None:
        if elem is None:
            return None
        else:
            value = elem.get(attr)
    if isinstance(value, str):
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
    return value


def _parse_dt_attr(
    elem: XmlElementLike | None, attr: str, value: Any | None
) -> datetime | Any | None:
    if value is None:
        if elem is None:
            return None
        else:
            value = elem.get(attr)
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y%m%dT%H%M%SZ")
        except ValueError:
            pass
    return value


def _export_dt(attr: str, value: datetime | str | Any) -> str:
    if isinstance(value, datetime):
        return value.strftime(r"%Y%m%d%TH%M%SZ")
    elif isinstance(value, str):
        try:
            datetime.strptime(value, r"%Y%m%d%TH%M%SZ")
            return value
        except ValueError:
            raise ValueError(
                f"Invalid value for '{attr}'. {value} does not follow the format YYYYMMDDTHHMMSSZ"
            )
    else:
        return str(value)


def _export_int(attr: str, value: int | str | Any) -> str:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        try:
            int(value)
            return value
        except ValueError:
            raise ValueError(f"Invalid value for '{attr}'. {value} is not an integer")
    else:
        return str(value)
