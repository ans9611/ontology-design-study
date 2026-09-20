import pytest

from ontostudy.bench import make_args
from ontostudy.queries import QUERIES
from ontostudy.schemas import SCHEMAS, VARIANTS
from ontostudy.synth import generate
import random


@pytest.fixture(scope="module")
def data():
    D = generate(300, seed=1)
    return D, {n: c(D) for n, c in SCHEMAS.items()}, make_args(D, random.Random(1), 3)


def test_generator_is_deterministic():
    a, b = generate(200, 3), generate(200, 3)
    assert a.knows == b.knows and [p["id"] for p in a.posts] == [p["id"] for p in b.posts]


@pytest.mark.parametrize("qid", list(QUERIES))
def test_all_schemas_agree(data, qid):
    D, schemas, args = data
    answers = {n: [QUERIES[qid](S, a) for a in args] for n, S in schemas.items()}
    assert answers["flat"] == answers["mid"] == answers["normalized"]


def test_normalized_costs_about_twice_mid_on_friends(data):
    D, schemas, _ = data
    p = D.persons[5]["id"]
    for S in schemas.values():
        S.G.reset(); S.friends(p)
    assert schemas["normalized"].G.hops >= 2 * schemas["mid"].G.hops - 2


def test_flat_reverse_lookup_scans(data):
    D, schemas, _ = data
    city = D.cities[0]["name"]
    for S in schemas.values():
        S.G.reset(); S.persons_in_city(city)
    assert schemas["flat"].G.hops >= len(D.persons)
    assert schemas["mid"].G.hops < len(D.persons)


def test_flat_indexed_agrees_and_answers_reverse_lookups_without_a_scan(data):
    D, schemas, args = data
    S = VARIANTS["flat_indexed"](D)
    for qid, fn in QUERIES.items():
        assert [fn(S, a) for a in args] == [fn(schemas["mid"], a) for a in args], qid
    S.G.reset(); S.persons_in_city(D.cities[0]["name"])
    assert S.G.hops < len(D.persons)
    assert S.G.nbytes() > schemas["flat"].G.nbytes()


def test_skew_concentrates_fan_in_and_keeps_answers_consistent():
    D0, D1 = generate(300, seed=1), generate(300, seed=1, skew=1.0)
    top = lambda D: max(sum(p["cityId"] == c["id"] for p in D.persons) for c in D.cities)
    assert top(D1) > 2 * top(D0)
    schemas = {n: c(D1) for n, c in {**SCHEMAS, **VARIANTS}.items()}
    args = make_args(D1, random.Random(1), 3, weighted=True)
    for qid, fn in QUERIES.items():
        answers = [[fn(S, a) for a in args] for S in schemas.values()]
        assert all(x == answers[0] for x in answers), qid
