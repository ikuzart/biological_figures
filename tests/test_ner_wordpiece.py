from bfg.stages.ner_hf import _clean_wordpiece, _dedupe, _merge_wordpiece, _snap_to_words


def test_snap_to_words_reads_surface_string_from_offsets():
    # The pipeline word is lowercased and spaced. The offsets are exact.
    text = "Western blot of IL-6 in HeLa cells"
    entities = [
        {"word": "il - 6", "entity_group": "gene", "score": 0.9, "start": 16, "end": 20},
    ]
    out = _snap_to_words(text, entities)
    assert out[0]["word"] == "IL-6"


def test_snap_to_words_widens_fragments_and_keeps_best_label():
    # Yurt split as yu plus ##rt under two labels becomes one entity.
    text = "apical Yurt localisation"
    entities = [
        {"word": "yu", "entity_group": "Diagnostic_procedure", "score": 0.6, "start": 7, "end": 9},
        {"word": "##rt", "entity_group": "Sign_symptom", "score": 0.4, "start": 9, "end": 11},
    ]
    out = _snap_to_words(text, entities)
    assert len(out) == 1
    assert out[0]["word"] == "Yurt"
    assert (out[0]["start"], out[0]["end"]) == (7, 11)
    assert out[0]["entity_group"] == "Diagnostic_procedure"


def test_clean_wordpiece_strips_hash_prefix():
    assert _clean_wordpiece("##sh") == "sh"
    assert _clean_wordpiece("##oblot") == "oblot"
    assert _clean_wordpiece("hyperlipidemia") == "hyperlipidemia"
    assert _clean_wordpiece("  ##foo  ") == "foo"


def test_dedupe_collapses_repeats():
    input_ = [
        {"word": "p66Shc", "entity_group": "gene"},
        {"word": "p66Shc", "entity_group": "gene"},
        {"word": "SUMO2", "entity_group": "gene"},
    ]
    out = _dedupe(input_)
    assert len(out) == 2
    assert {e["word"] for e in out} == {"p66Shc", "SUMO2"}


def test_dedupe_is_case_insensitive():
    out = _dedupe(
        [
            {"word": "p66shc", "entity_group": "gene"},
            {"word": "p66Shc", "entity_group": "gene"},
        ]
    )
    assert len(out) == 1


def test_merge_wordpiece_stitches_touching_continuation():
    entities = [
        {"word": "p66", "entity_group": "gene", "score": 0.9, "start": 0, "end": 3},
        {"word": "##shc", "entity_group": "gene", "score": 0.8, "start": 3, "end": 8},
    ]
    merged = _merge_wordpiece(entities)
    assert len(merged) == 1
    assert merged[0]["word"] == "p66shc"
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 8
    assert merged[0]["score"] == 0.8


def test_merge_wordpiece_stitches_multiple_continuations():
    entities = [
        {"word": "p66", "entity_group": "gene", "score": 0.9, "start": 0, "end": 3},
        {"word": "##s", "entity_group": "gene", "score": 0.85, "start": 3, "end": 4},
        {"word": "##hc", "entity_group": "gene", "score": 0.8, "start": 4, "end": 6},
    ]
    merged = _merge_wordpiece(entities)
    assert len(merged) == 1
    assert merged[0]["word"] == "p66shc"
    assert merged[0]["end"] == 6


def test_merge_wordpiece_drops_orphan_continuation():
    entities = [
        {"word": "IB", "entity_group": "protein", "score": 0.9, "start": 0, "end": 2},
        {"word": "##oblot", "entity_group": "technique", "score": 0.7, "start": 20, "end": 26},
    ]
    merged = _merge_wordpiece(entities)
    assert len(merged) == 1
    assert merged[0]["word"] == "IB"


def test_merge_wordpiece_does_not_merge_across_gaps():
    entities = [
        {"word": "p66", "entity_group": "gene", "score": 0.9, "start": 0, "end": 3},
        {"word": "##shc", "entity_group": "gene", "score": 0.8, "start": 10, "end": 15},
    ]
    merged = _merge_wordpiece(entities)
    assert [e["word"] for e in merged] == ["p66"]


def test_merge_wordpiece_strips_stray_marker_inside_token():
    entities = [
        {"word": "p66##shc", "entity_group": "gene", "score": 0.9, "start": 0, "end": 8},
    ]
    merged = _merge_wordpiece(entities)
    assert merged[0]["word"] == "p66shc"
