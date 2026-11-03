"""Read-only, source-relative duplicate and lineage audit of discovery rows.

An audit cluster is *not* a reconciled Work, a count of independent sources,
or an admission decision.  Source observations must remain in the catalog.
"""

import argparse
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")

# Conservative independence families: alternate labels for one upstream
# publisher do not create independent corroboration.  This is an audit mapping,
# not an assertion that all pages or third-party studios have one legal owner.
FAMILIES = {
    "publisher:paramount": "paramount-publisher-family",
    "publisher:paramountplus.com": "paramount-publisher-family",
    "publisher:startrek.com": "paramount-publisher-family",
    "publisher:simonandschuster.com": "simonandschuster-publisher-family",
    "distributor:penguinrandomhouse.com:titan-books": "prh-distributor-family",
    "wikidata:wdqs": "wikidata-wdqs-family",
}

# A publisher label alone is not provenance: it must agree with the URL host.
# Conservative exceptions for Paramount-attributed Shorts and Mikros studio
# title-list observations retain their existing source-relative attribution;
# they are not additional independent corporate witnesses.
SOURCE_HOSTS = {
    "publisher:paramount": frozenset({"www.paramountplus.com", "www.startrek.com",
                                       "www.mikrosanimation.com", "youtu.be"}),
    "publisher:paramountplus.com": frozenset({"www.paramountplus.com"}),
    "publisher:startrek.com": frozenset({"www.startrek.com"}),
    "publisher:simonandschuster.com": frozenset({"www.simonandschuster.com"}),
    "distributor:penguinrandomhouse.com:titan-books": frozenset({"www.penguinrandomhouse.com"}),
    "wikidata:wdqs": frozenset({"www.wikidata.org"}),
}


def _norm(value):
    """Normalize text for a *candidate overlap*, never global identity."""
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def audit_rows(rows):
    """Pure audit, failing closed on missing/ambiguous metadata or admission."""
    by_signature = defaultdict(list)
    by_locator = defaultdict(list)
    ids = set()

    for row in rows:
        row_id = row.get("row_id")
        if not isinstance(row_id, str) or not row_id or row_id in ids:
            raise ValueError(f"missing/duplicate source-local row_id: {row_id!r}")
        ids.add(row_id)
        group = row.get("source_group")
        if group not in FAMILIES:
            raise ValueError(f"unreviewed source independence group in {row_id}: {group!r}")
        for key in ("medium", "context", "title", "source_input"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"missing source-relative {key} in {row_id}")
        if (row.get("identity_scope") != "SOURCE_LOCAL" or
                row.get("verification_status") != "UNVERIFIED_METADATA" or
                row.get("admission_effect") != "NONE" or
                row.get("coverage_effect") != "NONE"):
            raise ValueError(f"discovery-only boundary violated in {row_id}")
        locator = row.get("source_locator")
        if locator is None:
            if group != "wikidata:wdqs":
                raise ValueError(f"non-Wikidata source locator missing in {row_id}")
            continue  # no URL witness to compare, not a duplicate signature
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError(f"invalid source locator in {row_id}")
        parsed = urlsplit(locator)
        if (parsed.scheme != "https" or not parsed.netloc or parsed.hostname not in SOURCE_HOSTS[group] or
                parsed.port is not None or parsed.username or parsed.password or
                parsed.query or parsed.fragment or not parsed.path.startswith("/")):
            raise ValueError(f"source host/lineage mismatch or invalid locator in {row_id}")

        # Exact URL deliberately retained: we cannot conclude two distinct
        # links identify the same source without independently reviewing them.
        signature = (row["medium"], _norm(row["context"]),
                     _norm(row["title"]), locator)
        by_signature[signature].append(row)
        by_locator[locator].append(row)

    duplicates = []
    for signature, cluster in sorted(by_signature.items()):
        if len(cluster) < 2:
            continue
        duplicates.append({
            "medium": signature[0], "context_normalized": signature[1],
            "title_normalized": signature[2], "source_locator": signature[3],
            "row_ids": sorted(row["row_id"] for row in cluster),
            "source_groups": sorted({row["source_group"] for row in cluster}),
            "independence_families": sorted({FAMILIES[row["source_group"]] for row in cluster}),
        })

    # Same exact URL + different textual group label: do not treat as two
    # independent witnesses even when no normalized title signature overlaps.
    alias_urls = []
    for url, cluster in sorted(by_locator.items()):
        groups = sorted({row["source_group"] for row in cluster})
        if len(groups) > 1:
            families = sorted({FAMILIES[group] for group in groups})
            if len(families) != 1:
                raise ValueError(f"one source URL assigned incompatible independence families: {url}")
            alias_urls.append({
                "source_locator": url,
                "source_groups": groups,
                "independence_families": families,
                "row_ids": sorted(row["row_id"] for row in cluster),
            })

    return {
        "audit_status": "SOURCE_LOCAL_ONLY_NO_ADMISSION",
        "row_count": len(rows),
        "unique_source_locator_count": len(by_locator),
        "source_group_counts": dict(sorted(Counter(row["source_group"] for row in rows).items())),
        "independence_family_counts": dict(sorted(Counter(FAMILIES[row["source_group"]]
                                                           for row in rows).items())),
        "duplicate_signature_count": len(duplicates),
        "duplicate_extra_row_count": sum(len(c["row_ids"]) - 1 for c in duplicates),
        "duplicate_signatures": duplicates,
        "same_url_multiple_source_groups": alias_urls,
        "disclaimer": "Discovery observations only; not distinct Works, independent witnesses, or verified source content.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="print full deterministic JSON audit")
    args = parser.parse_args(argv)
    catalog = json.loads((args.repo_root / CATALOG).read_text(encoding="utf-8"))
    result = audit_rows(catalog["rows"])
    if catalog.get("row_count") != result["row_count"]:
        raise ValueError("discovery catalog row_count does not match rows")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"Source-local rows: {result['row_count']}; distinct URL locators: "
              f"{result['unique_source_locator_count']}; overlap signatures: "
              f"{result['duplicate_signature_count']} "
              f"({result['duplicate_extra_row_count']} extra observations); "
              f"multi-label URLs: {len(result['same_url_multiple_source_groups'])}")
        print(result["disclaimer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
