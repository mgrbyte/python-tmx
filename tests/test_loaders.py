import bz2
import gzip
import lzma
import tempfile
import typing as t
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

import requests

CACHE_DIR: Path = Path("~/.cache/python-tmx/test_files")


DECOMPRESSORS = {".gz": gzip.decompress, ".xz": lzma.decompress, ".bz2": bz2.decompress}


@contextmanager
def cached_remote_tmx_file(tmx_url: str):
    local_tmx_file_path = CACHE_DIR.expanduser() / Path(
        urlparse(tmx_url).path.lstrip("/")
    )
    compression: str | None = None
    if not local_tmx_file_path.suffix == ".tmx":
        suffixes = list(local_tmx_file_path.suffixes)
        suffixes.remove(".tmx")
        compression = "".join(suffixes)
        local_tmx_file_path = local_tmx_file_path.with_name(local_tmx_file_path.stem)
    if not local_tmx_file_path.is_file():
        local_tmx_file_path.parent.mkdir(exist_ok=True, parents=True)
        with requests.get(tmx_url, stream=True) as response:
            if compression:
                decompressor = DECOMPRESSORS[compression]
                data = decompressor(response.content)
            else:
                data = response.content
            local_tmx_file_path.write_bytes(data)
    yield local_tmx_file_path


def test_load_tmx_export_roundtrip():
    from tmx.loaders import load_tmx
    from tmx.structural import tmx, tuv

    def flatten_segments(tmx_obj: tmx) -> t.Iterator[tuv]:
        for tu_obj in tmx_obj.tus:
            for tuv_obj in tu_obj.tuvs:
                yield from tuv_obj.runs

    with cached_remote_tmx_file(
        "https://object.pouta.csc.fi/OPUS-XLEnt/v1.2/tmx/cy-en.tmx.gz"
    ) as tmx_file:
        tmx_obj_loaded = load_tmx(tmx_file)
        assert isinstance(tmx_obj_loaded, tmx)
        with tempfile.NamedTemporaryFile(mode="wb+") as tf:
            tmx_obj_loaded.export(tf.name)
            tf.seek(0)
            tmx_obj_exported = load_tmx(tf.name)
        loaded_segments = [seg.text for seg in flatten_segments(tmx_obj_loaded)]
        exported_segemnts = [seg.text for seg in flatten_segments(tmx_obj_exported)]
        assert loaded_segments == exported_segemnts
