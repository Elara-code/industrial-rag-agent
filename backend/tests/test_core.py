import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from app.main import can_access, normalize_text, split_chunks


def test_normalize_japanese_spacing():
    assert normalize_text("　E-204\n 手順 ") == "e-204 手順"


def test_permission_filter():
    assert can_access("生产部", ["生产部"], "DEPARTMENT")
    assert not can_access("维修部", ["生产部"], "DEPARTMENT")
    assert can_access("维修部", ["生产部"], "PROJECT_PUBLIC")


def test_chunking_has_bounded_chunks():
    chunks = split_chunks("a" * 10 + "\n" + "b" * 10, size=12)
    assert len(chunks) == 2 and all(len(chunk) <= 12 for chunk in chunks)
