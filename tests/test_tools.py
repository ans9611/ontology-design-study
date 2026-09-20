from ontostudy.check_refs import norm, parse_bib
from ontostudy.slr import STRINGS


def test_norm_strips_latex_accents_and_unicode():
    assert norm(r"Vrande{\v{c}}i{\'c}") == norm("Vrandečić") == "vrandecic"
    assert norm(r"P{\'e}rez") == "perez"


def test_parse_bib_reads_fields():
    entries = parse_bib("@article{k1,\n  author = {A, B and C, D},\n  title = {T},\n  year = {2001}\n}\n")
    assert entries == [{"key": "k1", "author": "A, B and C, D", "title": "T", "year": "2001"}]


def test_search_strings_cover_all_rqs():
    assert set(STRINGS) == {"S1", "S2", "S3"}


def test_site_data_matches_the_tables():
    from ontostudy.site import build

    d = build()
    assert len(d["rq1"]["rows"]) == 7 and len(d["rq1"]["columns"]) == 6
    assert [c["id"] for c in d["rq2"]["cases"]] == ["google-kg", "amazon", "wikidata", "freebase", "schema-org", "gene-ontology", "snomed-ct", "cyc"]
    assert d["rq2"]["cases"][3]["outcome"] == "abandoned"
    assert len(d["rq3"]["queries"]) == 20 and len(d["rq3"]["bench"]) == len(d["rq3"]["scales"]) * 3 * 20
    assert [h["verdict"] for h in d["rq3"]["hypotheses"]] == ["supported", "supported", "refuted as stated", "partly refuted"]
    assert [g["id"] for g in d["guidelines"]] == [f"G{i}" for i in range(1, 13)]
    assert [r["n"] for r in d["references"]] == list(range(1, 28)) and d["references"][0]["doi"] == "10.1006/knac.1993.1008"
    sg = d["schemas"]
    assert [len(sg[s]["types"]) for s in ("flat", "mid", "normalized")] == [4, 9, 22]
    assert len(sg["flat"]["sample"]["nodes"]) < len(sg["mid"]["sample"]["nodes"]) < len(sg["normalized"]["sample"]["nodes"])
    assert {n["id"] for n in sg["mid"]["sample"]["nodes"]} <= {n["id"] for n in sg["normalized"]["sample"]["nodes"]}


def test_report_renders_every_marker_from_csvs():
    from ontostudy.report import build_blocks, render

    blocks = build_blocks()
    assert {"headline", "per-query", "sizes"} <= set(blocks)
    text = "<!-- table:headline -->\nold\n<!-- /table -->\n\n<!-- table:nope -->\nkeep\n<!-- /table -->"
    out = render(text, blocks)
    assert "old" not in out and "keep" in out and "| median hop ratio" in out


def test_cost_model_fits_both_engines():
    from ontostudy.report import cost_model

    fits = cost_model()
    assert fits and set(fits) >= {"python", "kuzu"}
    assert fits["python"]["n"] == 360 and fits["python"]["r2"] > 0.8
    assert all(0 <= m["r2"] <= 1 for m in fits.values())
