import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from app.main import (
    answer_matches_facts,
    can_access,
    citation_score,
    has_exact_fact_conflict,
    merge_ranked,
    normalize_text,
    split_chunks,
)


def test_normalize_japanese_spacing():
    assert normalize_text("　E-204\n 手順 ") == "e-204 手順"


def test_permission_filter():
    assert can_access("生产部", ["生产部"], "DEPARTMENT")
    assert not can_access("维修部", ["生产部"], "DEPARTMENT")
    assert can_access("维修部", ["生产部"], "PROJECT_PUBLIC")


def test_chunking_has_bounded_chunks():
    chunks = split_chunks("a" * 10 + "\n" + "b" * 10, size=12)
    assert len(chunks) == 2 and all(len(chunk) <= 12 for chunk in chunks)


def test_rrf_prefers_consistent_results():
    assert merge_ranked(["a", "b"], ["b", "a"], ["b"])[0] == "b"


def test_answer_matching_allows_sentence_variants_but_rejects_exact_fact_changes():
    assert answer_matches_facts("装置主電源をOFFにして、5分以上冷却してください。", "装置主電源をOFFにし、5分以上冷却する")
    assert answer_matches_facts("交換推奨は8000運転時間です。", "8000運転時間")
    assert not answer_matches_facts("交換推奨は6000運転時間です。", "8000運転時間")
    assert not answer_matches_facts("エラーはE-205です。", "E-204")


def test_semantic_fallback_blocks_conflicting_exact_facts():
    assert not has_exact_fact_conflict("装置主電源をOFFにして、5分以上冷却してください。", "装置主電源をOFFにし、5分以上冷却する")
    assert not has_exact_fact_conflict("交換推奨は8000运行小时です。", "8000運転時間")
    assert has_exact_fact_conflict("交換推奨は6000运行小时です。", "8000運転時間")
    assert has_exact_fact_conflict("エラーはE-205です。", "E-204")


def test_citation_score_requires_source_page_and_supporting_fact():
    evidence = [
        {"document_filename": "manual.pdf", "page": 4, "text": "E-204は冷却水温センサー回路異常を示す。"},
        {"document_filename": "manual.pdf", "page": 5, "text": "E-205はモータ負荷過大。"},
    ]
    score = citation_score(["manual.pdf:p4"], "冷却水温センサー回路異常", evidence)
    assert score == {"document_hit": 1.0, "page_hit": 1.0, "chunk_precision": 0.5, "supported": 1, "shown": 2}
