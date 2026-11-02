#!/usr/bin/env python3
"""Build a separate, proposal-only publisher discovery index.

The manifest allowlists exact in-repository bytes; the hash authenticates
local file identity ONLY. It does not attest remote page capture, rights,
publisher independence, complete rosters, Work admission, or continuity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import sys
from datetime import date
from pathlib import Path

if __package__:
    from . import build_research_leads as discovery
    from . import validate_publisher_episode_roster as roster_validator
else:
    import build_research_leads as discovery
    import validate_publisher_episode_roster as roster_validator


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = Path("registry/public_discovery_sources.json")
# Deliberately outside explorer/: the Pages workflow has an exact allowlist
# and this candidate-only research derivative is not yet a deployed UI asset.
OUTPUT = Path("proposals/discovery/publisher-catalog.json")
SHA = re.compile(r"[0-9a-f]{64}\Z")
FORMATS = {"PUBLISHER_EPISODE_SLOTS_V1", "TNG_PUBLISHER_REFERENCES_V1"}
MAX_SOURCES = 24
TNG_SOURCE_KINDS = {
    "OFFICIAL_VIDEO_PAGE_METADATA",
    "OFFICIAL_PREVIEW_PAGE_METADATA",
    "OFFICIAL_EDITORIAL_RETROSPECTIVE_METADATA",
    "OFFICIAL_WATCH_GUIDE_REFERENCE_METADATA",
}
SFA_PUBLISHER = "Paramount+"
SFA_INDEPENDENCE_GROUP = "publisher:paramount"
SFA_PRIMARY_PREFIX = "https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/"
SFA_CROSSCHECK = "https://www.paramountpressexpress.com/paramount-plus/shows/star-trek-starfleet-academy/episodes/"


def _obj(value: object, names: set[str], where: str) -> dict:
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError(f"{where}: missing or unexpected keys")
    return value


def _safe_text(value: object, where: str, max_length: int = 160) -> str:
    return roster_validator.text(value, where, max_length)


def _load(root: Path, path: Path, max_bytes: int = 512_000) -> dict:
    return discovery._strict_json(discovery.safe_read(root, path, max_bytes=max_bytes), str(path))


def _publisher_slots(data: dict, path: str, catalog: dict) -> list[dict]:
    roster_validator.validate(data, catalog)
    batch_id = data["batch_id"]
    mission = data["mission_id"]
    observation = data["observation"]
    independence = observation["independence_group"]
    # This first supported format is specifically Starfleet Academy's one
    # Paramount lineage, not a generic authority claim from an arbitrary host.
    if (mission != "sfa" or observation["publisher"] != SFA_PUBLISHER
            or independence != SFA_INDEPENDENCE_GROUP
            or not observation["primary_locator"].startswith(SFA_PRIMARY_PREFIX)
            or observation["crosscheck_locator"] != SFA_CROSSCHECK):
        raise ValueError(f"{path}: unsupported SFA publisher lineage")
    return [{
        "row_id": f"{batch_id}:S{slot['season']}E{slot['episode_number']}",
        "mission_id": mission,
        "source_batch_id": batch_id,
        "source_bundle_path": path,
        "independence_group": independence,
        "publisher": observation["publisher"],
        "source_locator": observation["primary_locator"],
        "source_page_title": None,
        "proposed_title": slot["title"],
        "season_number": slot["season"],
        "episode_number": slot["episode_number"],
        "observation_kind": "PUBLISHER_EPISODE_SLOT_METADATA",
        "observed_on": observation["observed_on"],
        "verification_status": "UNVERIFIED_METADATA",
        "coverage_effect": "NONE",
    } for slot in data["episode_slots"]]


def _tng_references(data: dict, path: str, catalog: dict) -> list[dict]:
    _obj(data, {"batch_id", "proposal_status", "sources", "works", "bindings",
                "crosswalks", "analysis_passes"}, f"{path}: proposal")
    if data["proposal_status"] != "PROPOSAL_ONLY_NOT_ADMITTED" or data["analysis_passes"] != []:
        raise ValueError(f"{path}: TNG references must remain unadmitted")
    batch = _safe_text(data["batch_id"], "batch_id", 120)
    if not batch.startswith("TNG-OFFICIAL-METADATA-"):
        raise ValueError(f"{path}: unsupported TNG batch")
    if "tng" not in {m["id"] for m in catalog["missions"]}:
        raise ValueError("Mission catalog lacks tng")
    sources, works, bindings = data["sources"], data["works"], data["bindings"]
    if not all(isinstance(rows, list) and 1 <= len(rows) <= 100 for rows in (sources, works, bindings)):
        raise ValueError(f"{path}: invalid or oversized TNG references")
    source_by_id, work_by_id = {}, {}
    for source in sources:
        if not isinstance(source, dict) or source.get("status") != "PROPOSED" or source.get("record_type") != "source":
            raise ValueError(f"{path}: source admission forbidden")
        source_id = _safe_text(source.get("source_id"), "source ID")
        if source_id in source_by_id or not source_id.startswith("proposal:tng:source:"):
            raise ValueError(f"{path}: duplicate or foreign TNG source")
        metadata = source.get("provider_metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}: missing publisher metadata")
        _safe_text(metadata.get("observed_title"), "source page title")
        if source.get("provider") != "StarTrek.com" or source.get("independence_group") != "publisher:startrek.com":
            raise ValueError(f"{path}: unsupported publisher ownership")
        if (not isinstance(source.get("source_kind"), str)
                or source["source_kind"] not in TNG_SOURCE_KINDS
                or source.get("source_variant") != "WEB_METADATA_ONLY"
                or source.get("fixture_only") is not False or source.get("content_fingerprint") is not None):
            raise ValueError(f"{path}: source must remain unverified, nonfixture metadata")
        locator = roster_validator.safe_locator(source.get("locator"), "publisher source locator")
        if not locator.startswith("https://www.startrek.com/"):
            raise ValueError(f"{path}: unsupported publisher host")
        if source.get("content_hash") is not None or source.get("retrieved_at") is not None or source.get("source_version") is not None:
            raise ValueError(f"{path}: unverified publisher page cannot have capture claims")
        source_by_id[source_id] = source
    for work in works:
        if not isinstance(work, dict) or work.get("record_type") != "work" or work.get("status") != "PROPOSED" or work.get("work_type") != "EPISODE" or work.get("fixture_only") is not False or work.get("parent_work_id") is not None:
            raise ValueError(f"{path}: accepted or non-episode Work forbidden")
        work_id = _safe_text(work.get("work_id"), "proposed Work ID")
        if work_id in work_by_id or not work_id.startswith("proposal:tng:work:"):
            raise ValueError(f"{path}: duplicate or foreign Work")
        _safe_text(work.get("title"), "proposed title")
        work_by_id[work_id] = work
    result = []
    seen_sources = set()
    for binding in bindings:
        if not isinstance(binding, dict) or binding.get("record_type") != "source_work_binding" or binding.get("lifecycle") != "PROPOSED" or binding.get("mapping_role") != "METADATA_ONLY" or binding.get("fixture_only") is not False:
            raise ValueError(f"{path}: binding admission forbidden")
        sid, wid = binding.get("source_id"), binding.get("work_id")
        if not isinstance(sid, str) or not isinstance(wid, str) or sid not in source_by_id or wid not in work_by_id or sid in seen_sources:
            raise ValueError(f"{path}: foreign or duplicate source-to-Work proposal")
        seen_sources.add(sid)
        source, work = source_by_id[sid], work_by_id[wid]
        meta = source["provider_metadata"]
        season, episode = meta.get("observed_season"), meta.get("observed_episode")
        if (season is None) != (episode is None) or (season is not None and (
                type(season) is not int or type(episode) is not int or season <= 0 or episode <= 0)):
            raise ValueError(f"{path}: ambiguous episode ordinal")
        try:
            date.fromisoformat(_safe_text(meta.get("observed_on"), "observed_on", 10))
        except ValueError as exc:
            raise ValueError(f"{path}: invalid observed date") from exc
        result.append({
            "row_id": sid,
            "mission_id": "tng",
            "source_batch_id": batch,
            "source_bundle_path": path,
            "independence_group": source["independence_group"],
            "publisher": source["provider"],
            "source_locator": source["locator"],
            "source_page_title": meta["observed_title"],
            "proposed_title": work["title"],
            "season_number": season,
            "episode_number": episode,
            "observation_kind": _safe_text(source.get("source_kind"), "source kind"),
            "observed_on": meta["observed_on"],
            "verification_status": "UNVERIFIED_METADATA",
            "coverage_effect": "NONE",
        })
    if len(result) != len(sources) or len(work_by_id) != len(sources):
        raise ValueError(f"{path}: TNG source/binding cardinality mismatch")
    crosswalks = data["crosswalks"]
    if not isinstance(crosswalks, list) or len(crosswalks) != len(works):
        raise ValueError(f"{path}: unexpected crosswalk count")
    seen_targets = set()
    for crosswalk in crosswalks:
        if (not isinstance(crosswalk, dict) or crosswalk.get("record_type") != "external_crosswalk"
                or crosswalk.get("mapping_status") != "CANDIDATE" or crosswalk.get("target_kind") != "WORK"
                or crosswalk.get("fixture_only") is not False
                or crosswalk.get("external_system") != "WIKIDATA"
                or not str(crosswalk.get("independence_group", "")).startswith("wikidata:")
                or not isinstance(crosswalk.get("target_id"), str)
                or crosswalk["target_id"] not in work_by_id):
            raise ValueError(f"{path}: crosswalk cannot establish accepted identity")
        if crosswalk["target_id"] in seen_targets:
            raise ValueError(f"{path}: duplicate crosswalk candidate")
        seen_targets.add(crosswalk["target_id"])
    return result


def build_bytes(root: Path) -> bytes:
    discovery._validate_catalog(root)
    catalog = _load(root, Path("registry/mission_catalog.json"))
    if catalog.get("admission_status") != "DISPLAY_CATALOG_ONLY":
        raise ValueError("mission catalog must remain display-only")
    manifest = _obj(_load(root, ALLOWLIST, 30_000), {
        "schema_version", "publication_scope", "accepted_work_effect",
        "accepted_source_binding_effect", "coverage_effect", "denominator_effect", "sources",
    }, "publisher allowlist")
    if manifest["schema_version"] != "1.0.0" or manifest["publication_scope"] != "CANDIDATE_DISCOVERY_ONLY":
        raise ValueError("unsupported publisher allowlist scope")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        if manifest[key] != "NONE":
            raise ValueError(f"allowlist cannot promote {key}")
    sources = manifest["sources"]
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_SOURCES:
        raise ValueError("publisher sources must be bounded and nonempty")
    rows, receipts, seen_paths, seen_ids = [], [], set(), set()
    for entry in sources:
        _obj(entry, {"format", "path", "sha256"}, "allowlisted source")
        fmt, path, expected = entry["format"], entry["path"], entry["sha256"]
        if not isinstance(fmt, str) or fmt not in FORMATS or not isinstance(path, str) or not re.fullmatch(
                r"proposals/librarian/[a-z0-9-]+/bundle\.json", path):
            raise ValueError("unsupported or unsafe publisher bundle path/format")
        if path in seen_paths or not isinstance(expected, str) or not SHA.fullmatch(expected):
            raise ValueError("duplicate bundle or invalid SHA-256 pin")
        seen_paths.add(path)
        raw = discovery.safe_read(root, Path(path))
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"{path}: allowlisted bundle SHA-256 mismatch")
        bundle = discovery._strict_json(raw, path)
        if fmt == "PUBLISHER_EPISODE_SLOTS_V1":
            source_rows = _publisher_slots(bundle, path, catalog)
        else:
            source_rows = _tng_references(bundle, path, catalog)
        for row in source_rows:
            identity = (row["source_bundle_path"], row["row_id"])
            if identity in seen_ids:
                raise ValueError("duplicate source-local row identity")
            seen_ids.add(identity)
        rows.extend(source_rows)
        receipts.append({"format": fmt, "path": path, "sha256": expected, "candidate_row_count": len(source_rows)})
    rows.sort(key=lambda row: (row["source_bundle_path"],
                               row["season_number"] if row["season_number"] is not None else 1000,
                               row["episode_number"] if row["episode_number"] is not None else 10000,
                               row["row_id"]))
    receipts.sort(key=lambda item: item["path"])
    result = {
        "schema_version": "1.0.0",
        "status": "UNVERIFIED_PUBLISHER_DISCOVERY_ONLY",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "roster_completeness": "UNRESOLVED",
        "candidate_row_count": len(rows),
        "publisher_source_count": len(receipts),
        "source_receipts": receipts,
        "rows": rows,
    }
    return (json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def safe_write(root: Path, relative: Path, data: bytes) -> None:
    """Atomically replace a regular output via no-follow directory descriptors.

    Refuse symlinked ancestors and output leaves; never traverse or overwrite
    the symlink target even if an attacker changes the leaf between checks.
    Directories must already exist. This does not change admission authority.
    """
    if (root.is_symlink() or relative.is_absolute() or not relative.parts
            or any(part in (".", "..") for part in relative.parts)):
        raise ValueError("unsafe output root/path")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("platform lacks safe no-follow directory flags")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(root, flags)
    try:
        for part in relative.parent.parts:
            next_fd = os.open(part, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        try:
            old = os.stat(relative.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(old.st_mode):
                raise ValueError("output must be a regular non-symlink file")
        # Create in the already-opened directory; a renamed ancestor cannot
        # redirect creation to a symlink target. Rename also never follows a
        # destination leaf symlink, and the explicit lstat above rejects one.
        temp_name = f".publisher-catalog-{secrets.token_hex(12)}.tmp"
        fd = os.open(temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600,
                     dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, relative.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        finally:
            try:
                os.unlink(temp_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
    finally:
        os.close(directory_fd)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check committed output matches exactly")
    args = parser.parse_args(argv)
    try:
        generated = build_bytes(ROOT)
        if args.check:
            if discovery.safe_read(ROOT, OUTPUT, max_bytes=1_000_000) != generated:
                raise ValueError("publisher catalog differs from deterministic output")
        else:
            safe_write(ROOT, OUTPUT, generated)
    except (ValueError, OSError, roster_validator.Rejected) as exc:
        print(f"PUBLISHER_CATALOG_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"PUBLISHER_CATALOG_OK: {len(json.loads(generated)['rows'])} candidate-only source-local rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
