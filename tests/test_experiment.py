import pytest

from ontostudy.bench import make_args
from ontostudy.queries import QUERIES
from ontostudy.schemas import SCHEMAS
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
