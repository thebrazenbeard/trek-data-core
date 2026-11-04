#!/usr/bin/env python3
"""Offline, SHA-pinned review of *unmerged* held episode-guide proposal Git objects.

Default output contains counts, provenance and unresolved gaps ONLY. Held
paraphrase text can be written solely with explicit opt-in outside the repo.
This tool never admits Source/Work/Evidence, advances coverage, or publishes
canonical Explorer/Briefings output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "tools/held_episode_pr_sources.json"
SUMMARY = REPO / "docs/HELD_EPISODE_PR_REVIEW_SNAPSHOT.json"
SCHEMA = "trek-offline-draft-episode-review-v1"
SERIES_CODES = frozenset({"TNG", "DS9", "VOY", "ENT", "PIC", "DIS"})
ANOMALY_CODES = frozenset({"POSSIBLE_TITLE_DESCRIPTION_CROSS_ASSIGNMENT"})
SECURE_PARENT_SUPPORTED = (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
                           and all(operation in os.supports_dir_fd for operation in (os.open, os.stat, os.unlink)))


def require(condition, why):
    if not condition:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=json_pairs)
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f"invalid pinned JSON: {exc}") from exc


def canon(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def run_git(args, repo=REPO):
    proc = subprocess.run(["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode:
        raise ValueError(f"draft Git object unavailable: {' '.join(args)}; fetch the exact PR head into a local ref first")
    return proc.stdout


def validate_descriptor(item):
    require(isinstance(item, dict) and set(item) == {"pr", "commit", "path", "sha256", "profile", "expected_rows"},
            "draft source manifest descriptor schema drift")
    require(type(item["pr"]) is int and item["pr"] > 0 and type(item["expected_rows"]) is int
            and item["expected_rows"] > 0, "invalid PR/row count")
    for name in ("commit", "sha256"):
        require(type(item[name]) is str and re.fullmatch(r"[0-9a-f]{40}" if name == "commit" else r"[0-9a-f]{64}", item[name]),
                f"invalid pinned {name}")
    path = Path(item["path"])
    require(not path.is_absolute() and path.parts and ".." not in path.parts and path.suffix == ".json"
            and item["path"] == path.as_posix(), "unsafe proposal Git path")
    require(item["profile"] in {"TNG", "DS9_S2", "DS9_S3_S4", "VOY", "HELD_SIDECAR"}, "unknown source profile")


def read_manifest(path=MANIFEST):
    require(path.is_file() and not path.is_symlink(), "missing/symlinked draft manifest")
    obj = parse_json(path.read_bytes())
    require(type(obj) is dict and set(obj) == {"schema_version", "accepted_main_at_review", "admission_status", "sources"},
            "review snapshot envelope drift")
    require(obj["schema_version"] == "trek-held-draft-pr-source-snapshot-v1"
            and obj["admission_status"] == "UNMERGED_PR_PROPOSALS_NOT_ACCEPTED_RESEARCH"
            and type(obj["sources"]) is list and len(obj["sources"]) == 8, "draft manifest provenance drift")
    seen = set()
    for desc in obj["sources"]:
        validate_descriptor(desc)
        require(desc["pr"] not in seen, "duplicate PR in source manifest")
        seen.add(desc["pr"])
    return obj


def load_candidate(item, repo=REPO):
    validate_descriptor(item)
    raw = run_git(["show", f"{item['commit']}:{item['path']}"], repo)
    require(len(raw) < 4_000_000, f"oversized PR proposal: #{item['pr']}")
    require(digest(raw) == item["sha256"], f"pinned draft blob bytes changed: #{item['pr']}")
    obj = parse_json(raw)
    require(type(obj) is dict, f"non-object draft proposal: #{item['pr']}")
    return obj


def publisher_url(value):
    require(type(value) is str and value.startswith("https://www.paramountplus.com/shows/")
            and "?" not in value and "#" not in value, "publisher guide URL drift")
    return value


def note(item, *, row_id, series, season, ordinal, title, synopsis, guide, locator,
         digest_reported=None, identity_hold="UNRESOLVED", anomalies=()):
    require(type(row_id) is str and row_id.strip() and type(title) is str and title.strip(),
            "missing draft local ID/title")
    require(type(season) is int and season > 0 and type(ordinal) is int and ordinal > 0,
            "source-local ordinal not a positive integer")
    require(series in SERIES_CODES, "unrecognized source-local series code")
    require(synopsis is None or type(synopsis) is str and 25 <= len(synopsis) <= 350 and "\n" not in synopsis,
            "publisher paraphrase absent/malformed")
    require(digest_reported is None or type(digest_reported) is str and re.fullmatch(r"[0-9a-f]{64}", digest_reported),
            "publisher short-description fingerprint drift")
    require(type(locator) is str and locator.strip(), "source-relative locator missing")
    return {
        "draft_review_id": f"pr{item['pr']}:{row_id}", "candidate_pr": item["pr"],
        "candidate_commit_sha": item["commit"], "candidate_packet_path": item["path"],
        "candidate_packet_sha256": item["sha256"], "draft_state": "UNMERGED_HELD_SOURCE_LOCAL_NOT_ADMITTED",
        "medium": "EPISODE", "series": series, "season": season, "source_episode_ordinal": ordinal,
        "source_local_row_id": row_id, "publisher_card_title": title,
        "held_marketing_paraphrase": synopsis,
        "editorial_publication_approval": "NONE", "canonical_work_id": None,
        "publisher_guide_url": publisher_url(guide), "source_card_locator": locator,
        "publisher_description_sha256": digest_reported, "identity_hold": identity_hold,
        "unresolved_source_anomalies": list(anomalies),
        "publisher_family": "PARAMOUNT_CBS_CORPORATE_SINGLE_LINEAGE",
    }


def parse_candidate(item, obj):
    profile = item["profile"]
    rows = []
    gaps = []
    anomalies = []
    if profile == "TNG":
        require(obj.get("coverage_effect") == "NONE" and obj.get("new_works") == 0
                and obj.get("governed_research_admissions") == 0
                and obj.get("publisher_family") == "paramount_corporate_publisher_family"
                and obj.get("data_status", "").startswith("HELD_TNG_"), "TNG draft admission or source status promoted")
        cards = obj.get("records")
        require(type(cards) is list, "TNG cards missing")
        for row in cards:
            card = row["publisher_card"]
            require(row.get("admission_effect") == "NONE" and row.get("coverage_effect") == "NONE"
                    and row.get("global_work_identity") == "UNRESOLVED"
                    and row.get("synopsis_publication_status") == "PENDING_EDITORIAL_AND_SOURCE_REVIEW"
                    and row.get("evidence_frame") == "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION"
                    and row.get("source_custody", "").startswith("NO_")
                    and card.get("raw_webpage_sha256", card.get("current_raw_html_sha256")) is None,
                    "TNG source or identity hold promoted")
            title = row.get("title", row.get("publisher_title"))
            rows.append(note(item, row_id=row["source_local_row_id"], series="TNG",
                             season=card["season"], ordinal=card["episode"], title=title,
                             synopsis=row["original_editorial_paraphrase_held"], guide=card["guide_url"],
                             locator=f"publisher guide S{card['season']} E{card['episode']} > {title}",
                             digest_reported=card["rendered_description_sha256"],
                             identity_hold=row["global_work_identity"],
                             anomalies=[row.get("publisher_framing_anomaly")] if row.get("publisher_framing_anomaly") not in (None, "NONE") else []))
    elif profile == "DS9_S2":
        require(obj.get("proposal_only") is True and obj.get("accepted_work_effect") == "NONE"
                and obj.get("accepted_source_binding_effect") == "NONE"
                and obj.get("episode_research_coverage_effect") == "NONE"
                and obj.get("synopsis_publication_effect") == "NONE"
                and obj.get("admitted_briefings") == 0, "DS9 S2 draft promoted")
        src = obj["source"]
        require(src.get("full_primary_episode_audiovisual_or_script_read") is False
                and src.get("raw_html_bytes_pinned") is False, "DS9 S2 claimed episode/raw source custody")
        cards = obj.get("source_local_cards")
        require(type(cards) is list, "DS9 S2 cards missing")
        for row in cards:
            rows.append(note(item, row_id=row["id"], series="DS9", season=row["season"],
                             ordinal=row["episode"], title=row["official_title"],
                             synopsis=row["original_held_paraphrase"], guide=src["publisher_guide_url"],
                             locator=row["publisher_card_locator"]))
    elif profile == "DS9_S3_S4":
        require(obj.get("proposal_only") is True and obj.get("accepted_work_effect") == "NONE"
                and obj.get("accepted_source_binding_effect") == "NONE"
                and obj.get("episode_research_coverage_effect") == "NONE"
                and obj.get("synopsis_publication_effect") == "NONE"
                and obj.get("admitted_briefings") == 0 and obj.get("episode_census_claim") == "NONE",
                "DS9 S3/S4 draft or census promoted")
        src = obj["source"]
        require(src.get("raw_source_body_sha256") is None and src.get("raw_html_bytes_pinned") is False
                and src.get("full_episode_audiovisual_or_script_read") is False, "DS9 false source custody")
        slots = obj.get("source_local_episode_slots")
        entities = obj.get("local_entities")
        assertions = obj.get("assertions")
        evidence = obj.get("evidence")
        require(all(type(v) is list for v in (slots, entities, assertions, evidence)), "DS9 structural records missing")
        require(len({s["id"] for s in slots}) == len(slots), "DS9 duplicate slot ID")
        require(len({e["id"] for e in entities}) == len(entities), "DS9 duplicate local entity")
        require(len({a["id"] for a in assertions}) == len(assertions), "DS9 duplicate local assertion")
        require(len({e["id"] for e in evidence}) == len(evidence), "DS9 duplicate evidence")
        entity_to_slot = {entity["id"]: entity["slot_id"] for entity in entities}
        assert_by_slot = {}
        evidence_by_id = {ev["id"]: ev for ev in evidence}
        for assertion in assertions:
            require(assertion.get("status") == "PROPOSED_SOURCE_LOCAL"
                    and assertion.get("fictional_truth_scope") == "NOT_OBJECTIVELY_ASSERTED"
                    and assertion.get("predicate") == "PUBLISHER_GUIDE_DESCRIBES", "DS9 assertion promoted")
            slot_id = entity_to_slot.get(assertion["subject_local_entity_id"])
            require(slot_id and slot_id not in assert_by_slot, "DS9 assertion local identity conflict")
            assert_by_slot[slot_id] = assertion
            linked = evidence_by_id.get(assertion["supporting_evidence_id"])
            require(linked is not None and linked.get("local_entity_id") == assertion["subject_local_entity_id"],
                    "DS9 assertion lacks aligned source-relative evidence")
        require(len(assert_by_slot) == len(slots) and len(evidence) == len(slots), "DS9 missing held source evidence")
        gaps = obj.get("missing_publisher_ordinals_in_extraction")
        require(type(gaps) is list and all(type(g) is int and g > 0 for g in gaps)
                and obj.get("observed_card_count") == len(slots), "DS9 extraction/census drift")
        anomalies = obj.get("anomaly_hypotheses", [])
        require(type(anomalies) is list, "DS9 anomaly field not a list")
        for anomaly in anomalies:
            require(type(anomaly) is dict and set(anomaly) == {
                "hypothesis", "basis", "affected_source_ordinals", "resolution"}
                and anomaly["hypothesis"] in ANOMALY_CODES
                and anomaly["basis"] == "PUBLISHER_CARD_TITLE_TOPIC_VS_DESCRIPTION_ONLY"
                and anomaly["resolution"] == "UNRESOLVED_NO_EXTERNAL_VERIFICATION"
                and type(anomaly["affected_source_ordinals"]) is list
                and all(type(n) is int and n > 0 for n in anomaly["affected_source_ordinals"]),
                "unrecognized anomaly code or false resolution")
        for row in slots:
            require(row.get("work_ref") is None and row.get("work_binding_status") == "UNRESOLVED",
                    "DS9 canonical Work identity promoted")
            assertion = assert_by_slot[row["id"]]
            witness = evidence_by_id[assertion["supporting_evidence_id"]]
            require(witness.get("locator") == row["source_card_locator"]
                    and witness.get("description_sha256") == row["source_description_sha256"],
                    "DS9 slot/evidence source fingerprint misaligned")
            row_flags = ["POSSIBLE_TITLE_DESCRIPTION_CROSS_ASSIGNMENT" for a in anomalies
                         if row["source_episode_ordinal"] in a["affected_source_ordinals"]]
            require(row.get("title_description_alignment") in (None, "NOT_INDEPENDENTLY_CHECKED",
                    "SUSPECTED_MISMATCH_UNRESOLVED"), "unrecognized title alignment state")
            if row.get("title_description_alignment") == "SUSPECTED_MISMATCH_UNRESOLVED":
                row_flags.append(row["title_description_alignment"])
            rows.append(note(item, row_id=row["id"], series="DS9", season=row["season"],
                             ordinal=row["source_episode_ordinal"], title=row["publisher_title"],
                             synopsis=assertion["original_held_paraphrase"], guide=src["url"],
                             locator=row["source_card_locator"],
                             digest_reported=row["source_description_sha256"], anomalies=row_flags))
        require(not set(gaps).intersection({r["source_episode_ordinal"] for r in rows}),
                "DS9 missing ordinal improperly materialized")
    elif profile == "VOY":
        require(obj.get("status") == "HELD_PROPOSAL_ONLY" and obj.get("coverage_effect") == "NONE"
                and obj.get("global_work_identity_effect") == "NONE"
                and obj.get("rights_or_publication_effect") == "NONE"
                and obj.get("episode_source_read") is False, "VOY draft promoted")
        cards = obj.get("source_local_cards")
        require(type(cards) is list, "VOY source cards missing")
        for row in cards:
            require(row.get("work_id") is None and row.get("evidence_state") == "PUBLISHER_DISPLAY_ONLY_HELD"
                    and row.get("synopsis_status") == "HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW",
                    "VOY held card promoted")
            rows.append(note(item, row_id=row["id"], series="VOY", season=row["season"],
                             ordinal=row["source_ordinal"], title=row["source_title"],
                             synopsis=row["original_synopsis"], guide=obj["source"]["url"],
                             locator=row["locator"], digest_reported=row["blurb_sha256"],
                             identity_hold=row["title_reconciliation"]))
    elif profile == "HELD_SIDECAR":
        require(obj.get("schema_version") == "trek-held-publisher-guide-notes-v1"
                and obj.get("data_status") == "HELD_SOURCE_LOCAL_DERIVED_SIDECAR_NOT_CANONICAL"
                and obj.get("canonical_work_count_added") == 0
                and obj.get("canonical_briefing_count_added") == 0
                and obj.get("episode_coverage_effect") == "NONE"
                and obj.get("synopsis_publication_approval") == "NONE", "held derived sidecar promoted")
        cards = obj.get("notes")
        require(type(cards) is list and len(cards) == obj["source_local_observation_count"], "held sidecar count drift")
        for row in cards:
            require(row.get("canonical_work_id") is None and row.get("canonical_briefing_id") is None
                    and row.get("research_state") == "HELD_SOURCE_LOCAL_NOT_ADMITTED"
                    and row.get("review_state") in ("HELD_EDITORIAL_DRAFT", "WITHHELD_MULTIPART_IDENTITY"),
                    "held sidecar record promoted")
            rows.append(note(item, row_id=row["note_id"], series=row["series"], season=row["season"],
                             ordinal=row["episode"], title=row["source_local_title"],
                             synopsis=row["paraphrase"], guide=row["publisher_guide_url"],
                             locator=row["source_card_locator"], digest_reported=row["publisher_description_sha256"],
                             identity_hold=row["identity_hold"]))
    else:
        raise ValueError(f"unsupported proposal profile: {profile}")
    require(len(rows) == item["expected_rows"], f"draft packet cardinality drift PR#{item['pr']}")
    return rows, gaps, anomalies


def review(repo=REPO, manifest=None):
    manifest = manifest or read_manifest()
    require(run_git(["rev-parse", "main"], repo).decode().strip() == manifest["accepted_main_at_review"],
            "accepted main moved; reorient draft proposal review")
    cards, seen_slots, gaps, anomalies = [], {}, [], []
    for source in manifest["sources"]:
        rows, missing, conflicts = parse_candidate(source, load_candidate(source, repo))
        for row in rows:
            key = (row["series"], row["season"], row["source_episode_ordinal"])
            require(key not in seen_slots, f"overlapping draft publisher slot {key}: PR#{seen_slots.get(key)} / PR#{source['pr']}")
            seen_slots[key] = source["pr"]
            cards.append(row)
        if missing:
            gaps.append({"candidate_pr": source["pr"], "series": "DS9", "missing_publisher_ordinals_in_extraction": missing,
                         "interpretation": "EXTRACTION_GAP_NOT_ACCEPTED_EPISODE_CENSUS"})
        if conflicts:
            anomalies.extend({"candidate_pr": source["pr"], "hypothesis": "POSSIBLE_TITLE_DESCRIPTION_CROSS_ASSIGNMENT",
                              "affected_source_ordinals": a["affected_source_ordinals"], "resolution": a["resolution"]} for a in conflicts)
    cards.sort(key=lambda row: (row["series"], row["season"], row["source_episode_ordinal"], row["candidate_pr"]))
    counts = Counter(row["series"] for row in cards)
    summaries = Counter(row["candidate_pr"] for row in cards)
    withheld = sum(row["held_marketing_paraphrase"] is None for row in cards)
    summary = {
        "schema_version": SCHEMA, "source_state": "DRAFT_PR_GIT_OBJECTS_NOT_ACCEPTED_MAIN",
        "accepted_main_at_review": manifest["accepted_main_at_review"],
        "candidate_snapshot_pr_count": len(manifest["sources"]),
        "source_local_observation_count": len(cards),
        "held_paraphrase_count": len(cards) - withheld,
        "withheld_identity_count": withheld,
        "by_series_observations": dict(sorted(counts.items())),
        "by_pr_observations": {str(pr): count for pr, count in sorted(summaries.items())},
        "provenance": manifest["sources"], "missing_extraction_ordinals": gaps,
        "unresolved_description_alignment_hypotheses": anomalies,
        "accepted_work_effect": "NONE", "accepted_evidence_effect": "NONE",
        "canonical_briefing_effect": "NONE", "synopsis_publication_approval": "NONE",
        "episode_coverage_effect": "NONE",
        "denominator_note": "Counts source-local draft publisher-card observations, not distinct accepted Works, episodes, full-source reads, or coverage.",
        "publisher_lineage_note": "All selected observations derive from the Paramount/CBS corporate publisher family; not independent corroborations.",
    }
    return summary, cards


def private_parent_supported():
    return SECURE_PARENT_SUPPORTED


def require_private_parent_binding(parent_fd, output, repo):
    """Confirm the public pathname still denotes the pinned *outside* parent."""
    try:
        current = output.parent.stat(follow_symlinks=False)
        pinned = os.fstat(parent_fd)
        require(stat.S_ISDIR(current.st_mode)
                and (current.st_dev, current.st_ino) == (pinned.st_dev, pinned.st_ino),
                "private output parent changed during write")
        require(not output.parent.resolve().is_relative_to(repo.resolve()),
                "private output parent redirected into repository")
    except OSError as exc:
        raise ValueError("private output parent changed or became unavailable") from exc


def secure_private_output(output, payload, repo):
    """Use an open directory capability, never the mutable output pathname."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_fd = os.open(output.anchor, flags)
    try:
        for component in output.parent.parts[1:]:
            try:
                next_fd = os.open(component, flags, dir_fd=parent_fd)
            except OSError as exc:
                raise ValueError("private output symlink or non-directory parent refused") from exc
            os.close(parent_fd)
            parent_fd = next_fd
        require_private_parent_binding(parent_fd, output, repo)
        created_fd = None
        created_identity = None
        try:
            created_fd = os.open(output.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=parent_fd)
            created = os.fstat(created_fd)
            created_identity = (created.st_dev, created.st_ino)
            with os.fdopen(created_fd, "wb") as stream:
                created_fd = None
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            require_private_parent_binding(parent_fd, output, repo)
            final = os.stat(output.name, dir_fd=parent_fd, follow_symlinks=False)
            require(stat.S_ISREG(final.st_mode)
                    and (final.st_dev, final.st_ino) == created_identity,
                    "private output file entry changed during write")
        except BaseException:
            # Remove only the *new* file created via O_EXCL, never a user file.
            if created_fd is not None:
                os.close(created_fd)
            if created_identity is not None:
                try:
                    current = os.stat(output.name, dir_fd=parent_fd, follow_symlinks=False)
                    if (current.st_dev, current.st_ino) == created_identity:
                        os.unlink(output.name, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
            raise
    finally:
        os.close(parent_fd)


def trusted_private_output(output, payload, repo):
    """Windows compatibility only: requires a trusted, non-mutating path tree."""
    current = output.parent
    while current != current.parent:
        require(not current.is_symlink() and not (hasattr(current, "is_junction") and current.is_junction()),
                "private output symlink/junction parent refused")
        current = current.parent
    stable_parent = output.parent.resolve()
    require(not stable_parent.is_relative_to(repo.resolve()) and stable_parent.is_dir(),
            "private output trusted parent must be existing and outside repository")
    target = stable_parent / output.name
    require(not target.exists() and not target.is_symlink(), "private output requires new file")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    require(output.parent.resolve() == stable_parent, "private output trusted parent changed during write")


def private_output(path, cards, summary, repo=REPO, *, trusted_output_path=False):
    output = Path(os.path.abspath(path))
    require(not output.is_relative_to(repo.resolve()) and not repo.resolve().is_relative_to(output),
            "private held text output must not be inside or above the repository")
    require(output.name not in ("", ".", "..") and not output.exists() and not output.is_symlink(),
            "private output requires new file")
    require(not output.parent.resolve().is_relative_to(repo.resolve()),
            "private output parent resolved into repository")
    payload = canon({"summary": summary, "held_source_local_notes": cards}).encode()
    if private_parent_supported():
        secure_private_output(output, payload, repo)
    else:
        require(trusted_output_path,
                "private output needs no-follow dirfd support; Windows trusted path requires explicit --trusted-output-path")
        trusted_private_output(output, payload, repo)
    return digest(payload)


def accepted_pilot_preflight(repo=REPO):
    """Read-only accepted-main admission gate, separate from draft observations."""
    proc = subprocess.run([sys.executable, "-B", "tools/check_episode_pilot_readiness.py"],
                          cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(proc.returncode == 0, "accepted-main pilot diagnostic failed")
    result = parse_json(proc.stdout)
    require(result.get("report_kind") == "NONFIXTURE_EPISODE_PILOT_TECHNICAL_PREREQUISITES",
            "unexpected canonical pilot preflight contract")
    return {
        "overall_status": result["overall_status"],
        "accepted_nonfixture_episode_works": result["accepted_nonfixture_episode_works"],
        "automated_prerequisite_complete_works": result["automated_prerequisite_complete_works"],
        "approved_projection_hash_count": result["approved_projection_hash_count"],
        "source_bound_requirements_not_supplied_by_drafts": [
            "independently accepted episode Work and Source identities",
            "accepted Librarian EVIDENCE_BEARING Source-to-Work binding using exact BYTE_HASH",
            "rights-valid private source bytes and independently replayed custody receipt",
            "accepted DISCOVERED predecessor and separately reviewed SOURCE_BOUND event",
        ],
        "evidence_class": "REAL_ACCEPTED_MAIN_DIAGNOSTIC_NOT_PROPOSAL_ADMISSION",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-summary", action="store_true", help="compare checked-in counts-only audit")
    parser.add_argument("--write-summary", action="store_true", help="regenerate counts-only audit metadata")
    parser.add_argument("--private-output", type=Path, help="explicitly write unpublished drafts to a new file OUTSIDE the repository")
    parser.add_argument("--trusted-output-path", action="store_true",
                        help="Windows compatibility opt-in for trusted, non-mutating private output paths; weaker than POSIX dirfd isolation")
    args = parser.parse_args()
    require(not (args.check_summary and args.write_summary), "choose one summary mode")
    require(not args.trusted_output_path or args.private_output is not None,
            "--trusted-output-path requires --private-output")
    summary, cards = review()
    summary["accepted_main_admission_preflight"] = accepted_pilot_preflight()
    rendered = canon(summary)
    if args.check_summary:
        require(SUMMARY.is_file() and SUMMARY.read_text(encoding="utf-8") == rendered, "counts-only held review summary stale")
    if args.write_summary:
        SUMMARY.write_text(rendered, encoding="utf-8")
    if args.private_output:
        output_hash = private_output(args.private_output, cards, summary,
                                     trusted_output_path=args.trusted_output_path)
        print(f"PRIVATE_HELD_REVIEW_WRITTEN_SHA256={output_hash}")
    else:
        print(f"DRAFT_EPISODE_REVIEW: {len(cards)} observations / {summary['held_paraphrase_count']} unpublished paraphrases / {summary['withheld_identity_count']} identity hold; no acceptance or coverage effect")


if __name__ == "__main__":
    main()
