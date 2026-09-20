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
    assert len(d["rq3"]["queries"]) == 20 and len(d["rq3"]["bench"]) == 3 * 3 * 20
    assert [h["verdict"] for h in d["rq3"]["hypotheses"]] == ["supported", "supported", "refuted as stated", "partly refuted"]
