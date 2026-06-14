#!/usr/bin/env python3
"""Refresh Quasar citation counts in data/citations.toml using SerpApi.

Replaces the old `scholarly` implementation (update_citations.py), which Google
Scholar blocked when run unattended (see the disabled step in
.github/workflows/publish.yml). SerpApi proxies Google Scholar for us, so the
numbers stay identical to what Scholar reports.

Two figures are tracked:
  direct    - total citations to Quasar's own papers
  secondary - total citations received by the papers that cite Quasar
              (i.e. the downstream impact of the works that use Quasar)

Needs a SerpApi key in the SERPAPI_KEY environment variable.

Cost: 1 Author-API call + roughly (direct / 20 + #papers) Organic-API calls.
The script prints the exact call count it used so usage stays predictable.

The run fails hard (non-zero exit, toml untouched) on any API error or if a
count came back lower than what is already stored -- a partial/rate-limited
crawl must never overwrite the published numbers with an undercount.
"""

import os
import sys
import time
from pathlib import Path

import requests
import toml

AUTHOR_ID = "KZCTPYoAAAAJ"  # Quasar's Google Scholar profile (matches the link on content/publications/_index.md)
ENDPOINT = "https://serpapi.com/search.json"
PAGE_SIZE = 20            # Organic API caps `num` at 20
MAX_PAGES_PER_PAPER = 100  # safety cap: up to 2000 citing papers per paper

FN = Path(__file__).resolve().parent.parent / "data" / "citations.toml"

_call_count = 0


def serpapi_get(params):
    """One SerpApi request. Raises on any transport/API error."""
    global _call_count
    params = {**params, "api_key": API_KEY}
    resp = requests.get(ENDPOINT, params=params, timeout=60)
    _call_count += 1
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"SerpApi error: {data['error']}")
    return data


def get_quasar_papers():
    """Return [(title, cites_id, citation_count), ...] for every Quasar paper."""
    papers = []
    start = 0
    while True:
        data = serpapi_get({
            "engine": "google_scholar_author",
            "author_id": AUTHOR_ID,
            "num": 100,
            "start": start,
            "sort": "pubdate",
        })
        articles = data.get("articles", [])
        for art in articles:
            cited_by = art.get("cited_by") or {}
            count = cited_by.get("value") or 0
            cites_id = cited_by.get("cites_id")
            if count and not cites_id:
                raise RuntimeError(
                    f"Paper '{art.get('title')}' has {count} citations but no "
                    "cites_id; refusing to undercount."
                )
            papers.append((art.get("title", "<untitled>"), cites_id, count))
        # Stop when SerpApi reports no further page of articles.
        if not data.get("serpapi_pagination", {}).get("next"):
            break
        start += len(articles)
        if not articles:
            break
    return papers


def count_secondary_for(cites_id):
    """Sum the citation counts of every paper that cites `cites_id`."""
    total = 0
    for page in range(MAX_PAGES_PER_PAPER):
        data = serpapi_get({
            "engine": "google_scholar",
            "cites": cites_id,
            "num": PAGE_SIZE,
            "start": page * PAGE_SIZE,
        })
        results = data.get("organic_results", [])
        for res in results:
            cb = (res.get("inline_links") or {}).get("cited_by") or {}
            total += cb.get("total") or 0
        if len(results) < PAGE_SIZE:
            break
        time.sleep(0.2)  # be gentle on the upstream
    else:
        raise RuntimeError(
            f"Hit the {MAX_PAGES_PER_PAPER}-page cap for cites_id={cites_id}; "
            "raise MAX_PAGES_PER_PAPER."
        )
    return total


def main():
    global API_KEY
    API_KEY = os.environ.get("SERPAPI_KEY")
    if not API_KEY:
        sys.exit("SERPAPI_KEY environment variable is not set; aborting.")

    print("Fetching Quasar papers from Google Scholar via SerpApi...")
    papers = get_quasar_papers()
    direct = sum(count for _, _, count in papers)

    print(f"\nThere are currently {len(papers)} Quasar papers:")
    for title, _, count in papers:
        print(f"  [{count:>4}] {title}")
    print(f"\nDirect citations to Quasar papers: {direct}")

    # Project the secondary crawl cost before spending the calls.
    projected = sum(
        max(1, -(-count // PAGE_SIZE)) for _, cid, count in papers if cid
    )
    print(f"Crawling citing papers (~{projected} more API calls)...")

    secondary = 0
    for title, cites_id, count in papers:
        if not cites_id:
            continue
        secondary += count_secondary_for(cites_id)

    print(f"\nSecondary citations (papers citing the works that use Quasar): {secondary}")
    print(f"Total SerpApi calls used this run: {_call_count}")

    td = toml.load(FN)

    if direct < int(td["direct"]):
        sys.exit(
            f"Direct citations dropped ({direct} < {td['direct']}); "
            "likely a partial crawl. Leaving toml untouched."
        )
    if secondary < int(td["secondary"]):
        sys.exit(
            f"Secondary citations dropped ({secondary} < {td['secondary']}); "
            "likely a partial crawl. Leaving toml untouched."
        )

    td["direct"] = direct
    td["secondary"] = secondary
    with open(FN, "wt") as of:
        toml.dump(td, of)
    print(f"\nUpdated {FN}: direct={direct}, secondary={secondary}")


if __name__ == "__main__":
    main()
