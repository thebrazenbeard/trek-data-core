#!/usr/bin/env python3
"""Build the static Mission Explorer search index, with no network or implicit admission.

The default result is an explicitly unadmitted display catalog. An optional,
already governed projection must pass its hash receipt before any assertion or
Mission Briefing metadata is exposed. No transcript text is indexed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_OUTPUTS = (
    "entities.jsonl", "facts.jsonl", "relations.jsonl", "contested.jsonl",
    "unresolved.jsonl", "provenance.jsonl", "assertion_history.jsonl",
    "reconciliation_history.jsonl",
)
STATUS_FILES = {"facts.jsonl": "STABLE", "contested.jsonl": "CONTESTED", "unresolved.jsonl": "UNRESOLVED"}
APPROVED_HASHES = ROOT / "registry" / "approved_projection_hashes.json"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def load_missions(path: Path) -> list[dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("admission_status") != "DISPLAY_CATALOG_ONLY" or not obj.get("authority"):
        raise ValueError("Mission catalog must disclose display-only authority")
    missions = obj.get("missions")
    if not isinstance(missions, list) or not missions:
        raise ValueError("Mission catalog is empty")
    ids = set()
    for mission in missions:
        if set(mission) != {"id", "title", "focus"} or any(not isinstance(v, str) or not v.strip() for v in mission.values()):
            raise ValueError("Invalid Mission display record")
        if mission["id"] in ids:
            raise ValueError(f"Duplicate Mission id: {mission['id']}")
        ids.add(mission["id"])
    return sorted(missions, key=lambda m: m["title"].casefold())


def verified_projection(path: Path) -> tuple[dict, dict[str, list[dict]]]:
    """Reject partial/corrupt canonical projection bundles before indexing."""
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("record_type") != "projection_manifest":
        raise ValueError("Unrecognized projection manifest")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != set(CANONICAL_OUTPUTS):
        raise ValueError("Projection manifest is missing canonical outputs")
    rows = {}
    for name in CANONICAL_OUTPUTS:
        receipt = outputs[name]
        payload = (path / name).read_bytes()
        if receipt.get("hash") != sha256(payload):
            raise ValueError(f"Projection output hash mismatch: {name}")
        parsed = [json.loads(line) for line in payload.decode("utf-8").splitlines() if line.strip()]
        if receipt.get("count") != len(parsed) or any(not isinstance(row, dict) for row in parsed):
            raise ValueError(f"Projection output count/type mismatch: {name}")
        rows[name] = parsed
    expected = sha256(canonical({name: outputs[name]["hash"] for name in CANONICAL_OUTPUTS}).encode("utf-8"))
    if manifest.get("projection_hash") != expected:
        raise ValueError("Projection bundle identity mismatch")
    return manifest, rows


def bounded_metadata(value: object) -> str:
    """No unbounded passage, transcript, or character dialogue in the static index."""
    if not isinstance(value, (str, int, float, bool)) or len(str(value)) > 160:
        return ""
    return str(value).replace("\n", " ").replace("\r", " ")


def approved_hashes(path: Path) -> set[str]:
    """A projection hash needs an independently reviewed mainline allowlist entry.

    This checked-in receipt is not a digital signature; repository review and
    branch protection establish its authority outside this offline builder.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or set(record) != {"authority", "projection_hashes"} or record["authority"] != "REVIEWED_MAIN_PROJECTION_HASH_ALLOWLIST":
        raise ValueError("Unrecognized approved projection receipt")
    hashes = record["projection_hashes"]
    if (not isinstance(hashes, list)
            or any(not isinstance(v, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", v) for v in hashes)
            or len(hashes) != len(set(hashes))):
        raise ValueError("Invalid approved projection hash list")
    return set(hashes)


def build_index(catalog: Path, projection: Path | None = None, approved_receipts: Path = APPROVED_HASHES) -> dict:
    missions = load_missions(catalog)
    index = {
        "schema_version": "1.0.0",
        "build": {"data_status": "MISSION_CATALOG_ONLY", "projection_hash": None},
        "missions": missions,
        "briefings": [],
        "records": [],
    }
    if projection is None:
        return index

    manifest, bundle = verified_projection(projection)
    if manifest["projection_hash"] not in approved_hashes(approved_receipts):
        raise ValueError("Projection hash lacks a reviewed mainline admission receipt")
    mission_ids = {m["id"] for m in missions}
    title_ids = {m["title"].casefold(): m["id"] for m in missions}
    # Work metadata comes only from a projected assertion's evidence provenance.
    provenance = {}
    for row in bundle["provenance.jsonl"]:
        aid = row.get("assertion_id")
        if aid:
            provenance.setdefault(aid, []).append(row)

    briefings = {}
    definitions = {"source": {}, "work": {}, "binding": {}}
    records = []
    seen = set()
    for filename, default_status in STATUS_FILES.items():
        for fact in bundle[filename]:
            aid = fact.get("assertion_id")
            if not isinstance(aid, str) or not aid or aid in seen:
                raise ValueError("Missing or duplicate projected assertion id")
            seen.add(aid)
            references = provenance.get(aid)
            if not references:
                raise ValueError(f"Projected assertion lacks attributable evidence: {aid}")
            if fact.get("effective_assertion_status") != "ACCEPTED":
                raise ValueError(f"Projected assertion is not accepted: {aid}")
            status = fact.get("projection_status", default_status)
            if filename == "facts.jsonl" and status != "STABLE":
                raise ValueError(f"Stable projection file contains {status}: {aid}")
            if filename == "contested.jsonl" and status not in ("CONTESTED", "STRUCTURAL_PARADOX"):
                raise ValueError(f"Contested projection file contains {status}: {aid}")
            if filename == "unresolved.jsonl" and status != "UNRESOLVED":
                raise ValueError(f"Unresolved projection file contains {status}: {aid}")

            source_ids = set()
            work_ids = set()
            mission_candidates = set()
            briefing_candidates = set()
            for proof in references:
                evidence = proof.get("evidence_record") or {}
                work = proof.get("work_record") or {}
                source = proof.get("source_record") or {}
                binding = proof.get("source_work_binding_record") or {}
                if not source.get("source_id") or evidence.get("source_id") != source["source_id"]:
                    raise ValueError(f"Broken Source provenance for {aid}")
                if not work.get("work_id") or evidence.get("work_id") != work["work_id"]:
                    raise ValueError(f"Broken Work provenance for {aid}")
                if (binding.get("source_id") != source["source_id"]
                        or binding.get("work_id") != work["work_id"]
                        or binding.get("lifecycle") != "ACCEPTED"
                        or binding.get("mapping_role") != "EVIDENCE_BEARING"):
                    raise ValueError(f"Missing accepted Source-to-Work binding for {aid}")
                if (source.get("status") != "ACCEPTED" or work.get("status") != "ACCEPTED"
                        or source.get("fixture_only") is not False
                        or work.get("fixture_only") is not False
                        or binding.get("fixture_only") is not False
                        or evidence.get("fixture_only") is True
                        or (proof.get("assertion_record") or {}).get("fixture_only") is True):
                    raise ValueError(f"Synthetic or unadmitted Source/Work/evidence for {aid}")
                if proof.get("effective_assertion_status") != "ACCEPTED":
                    raise ValueError(f"Provenance assertion disposition mismatch for {aid}")
                for kind, identity, record in (("source", source["source_id"], source),
                                               ("work", work["work_id"], work),
                                               ("binding", binding.get("binding_id"), binding)):
                    if not identity:
                        raise ValueError(f"Missing {kind} identity in provenance for {aid}")
                    old = definitions[kind].setdefault(identity, canonical(record))
                    if old != canonical(record):
                        raise ValueError(f"Contradictory {kind} provenance metadata for {identity}")
                source_ids.add(source["source_id"])
                work_ids.add(work["work_id"])
                # Resolve each proof independently. A cross-Mission assertion may
                # cite episodes from multiple series without assigning one
                # series' episode to another or dropping later proofs.
                proof_missions = set()
                series = work.get("series")
                resolved = series if series in mission_ids else title_ids.get(str(series).casefold())
                if resolved:
                    proof_missions.add(resolved)
                lineage = proof.get("work_lineage_records", [])
                if not isinstance(lineage, list) or any(not isinstance(v, dict) for v in lineage):
                    raise ValueError(f"Invalid Work ancestry metadata for {aid}")
                for ancestor in lineage:
                    ancestor_id = title_ids.get(str(ancestor.get("title", "")).casefold())
                    if ancestor_id:
                        proof_missions.add(ancestor_id)
                if len(proof_missions) > 1:
                    raise ValueError(f"Conflicting Mission identity in Work ancestry for {aid}")
                mission_candidates.update(proof_missions)
                kind = {str(work.get(k)).upper() for k in ("medium", "work_type") if work.get(k)}
                if len(kind) > 1:
                    raise ValueError(f"Conflicting Work media classifications for {aid}")
                resolved = next(iter(proof_missions)) if proof_missions else None
                if resolved and "EPISODE" in kind:
                    candidate_id = work["work_id"]
                    briefing_candidates.add(candidate_id)
                    season, episode = work.get("season"), work.get("episode")
                    for number in (season, episode):
                        if number is not None and (type(number) is not int or not 1 <= number <= 9999):
                            raise ValueError(f"Invalid Mission Briefing numbering for {candidate_id}")
                    title = bounded_metadata(work.get("title"))
                    if not title:
                        raise ValueError(f"Invalid public Mission Briefing title for {candidate_id}")
                    briefing = {
                        "id": candidate_id,
                        "mission_id": resolved,
                        "title": title,
                        "season": season,
                        "episode": episode,
                        "work_id": candidate_id,
                        "admission_status": "EVIDENCED_IN_PROJECTION",
                    }
                    previous = briefings.setdefault(candidate_id, briefing)
                    if previous != briefing:
                        raise ValueError(f"Contradictory Mission Briefing identity for {candidate_id}")
            mission_id = next(iter(mission_candidates)) if len(mission_candidates) == 1 else None
            briefing_id = next(iter(briefing_candidates)) if len(briefing_candidates) == 1 else None
            if briefing_id and (not mission_id or briefings[briefing_id]["mission_id"] != mission_id):
                briefing_id = None
            # Display a bounded scalar object value, not copyrighted passages.
            title = f"{bounded_metadata(fact.get('predicate')) or 'Assertion'} · {bounded_metadata(fact.get('subject')) or 'Unknown subject'}"
            records.append({
                "id": aid, "title": title,
                "summary": bounded_metadata(fact.get("object")),
                "kind": "ASSERTION", "mission_id": mission_id,
                "briefing_id": briefing_id, "predicate": fact.get("predicate"),
                "source_ids": sorted(source_ids), "work_ids": sorted(work_ids),
                "projection_status": status,
            })

    index["build"] = {"data_status": "GOVERNED_PROJECTION", "projection_hash": manifest["projection_hash"]}
    index["briefings"] = sorted(briefings.values(), key=lambda b: (b["mission_id"], b["title"], b["id"]))
    index["records"] = sorted(records, key=lambda r: r["id"])
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "registry" / "mission_catalog.json")
    parser.add_argument("--projection-dir", type=Path, help="Optional governed, hash-verified canonical projection bundle")
    parser.add_argument("--out", type=Path, default=ROOT / "explorer" / "index.json")
    args = parser.parse_args()
    result = build_index(args.catalog, args.projection_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Explorer index: {len(result['missions'])} Missions, {len(result['briefings'])} evidenced Mission Briefings, {len(result['records'])} projected records")


if __name__ == "__main__":
    main()
