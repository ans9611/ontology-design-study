"""Verify every DOI in references.bib against Crossref.

For each entry with a DOI, fetches the Crossref record and compares title,
first author surname and year. Prints a table; exit code 1 if any mismatch.

    python -m ontostudy.check_refs
"""

from __future__ import annotations

import difflib
import json
import unicodedata
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
BIB = ROOT / "references" / "references.bib"


def parse_bib(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        fields = dict(re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*(?=\n|\w+\s*=)", m.group(3) + "\n", re.S))
        fields = {k: " ".join(v.split()) for k, v in fields.items()}
        out.append({"key": m.group(2).strip(), **fields})
    return out


def norm(s: str) -> str:
    # drop LaTeX accent commands, then strip diacritics via NFKD
    s = re.sub(r"\\[\"'^`~vc]\{?(\w)\}?", r"\1", s)
    s = re.sub(r"[{}\\]", "", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def crossref(doi: str) -> dict | None:
    req = urllib.request.Request(f"https://api.crossref.org/works/{doi}", headers={"User-Agent": "ontostudy/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["message"]
    except Exception:
        return None


def main() -> int:
    bad = 0
    print(f"{'key':22s} {'doi':40s} title  author  year")
    for e in parse_bib(BIB.read_text()):
        doi = e.get("doi")
        if not doi:
            print(f"{e['key']:22s} {'(no doi)':40s} -      -       -")
            continue
        m = crossref(doi)
        if not m:
            print(f"{e['key']:22s} {doi:40s} DOI NOT RESOLVED"); bad += 1; continue
        cr_main = norm((m.get("title") or [""])[0])
        cr_full = norm(" ".join((m.get("title") or [""]) + (m.get("subtitle") or [])))
        mine = norm(e.get("title", ""))
        t_ok = any(difflib.SequenceMatcher(None, mine, c).ratio() > 0.85 for c in (cr_main, cr_full)) or mine.startswith(cr_main)
        first = e.get("author", e.get("editor", "")).split(" and ")[0]
        surname = norm(first.split(",")[0])
        cr_auth = [norm(a.get("family", "")) for a in m.get("author", m.get("editor", []))]
        a_ok = (not cr_auth) or surname in cr_auth
        years = {str(((m.get(k) or {}).get("date-parts") or [[None]])[0][0]) for k in ("published-print", "published-online", "issued", "created")}
        years.discard("None")
        cr_year = "/".join(sorted(years))
        y_ok = str(e.get("year")) in years
        flag = "ok " if (t_ok and a_ok and y_ok) else "!! "
        print(f"{e['key']:22s} {doi:40s} {'ok' if t_ok else 'NO':5s}  {'ok' if a_ok else 'NO':6s}  {'ok' if y_ok else 'NO ('+cr_year+')'}   {flag}")
        if not (t_ok and a_ok and y_ok):
            bad += 1
            if not t_ok:
                print(f"{'':22s}   crossref title: {(m.get('title') or [''])[0]}")
    print(f"\n{bad} entries need attention")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
