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
