#!/usr/bin/env python3
"""Deterministic, source-local multimedia discovery index (never admission).

This display-only derivative intentionally counts *source observations*, not
distinct canonical Works or franchise-wide coverage. Cross-source rows are not
silently reconciled even if their titles resemble one another.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

if __package__:
    from . import build_film_catalog as films
    from . import build_literary_candidates as literature
    from . import build_legacy_s1_discovery as legacy1
    from . import build_legacy_s2_discovery as legacy
    from . import build_legacy_s3_discovery as legacy3
    from . import build_prodigy_publisher_discovery as prodigy
    from . import build_publisher_s4_discovery as season4
    from . import build_publisher_s5_discovery as season5
    from . import build_publisher_s6_discovery as season6
    from . import build_publisher_s7_discovery as season7
    from . import build_tas_publisher_roster as tas
    from . import build_prodigy_mikros_s1a_discovery as mikros
    from . import build_scouts_publisher_discovery as scouts
    from . import build_publisher_catalog as publisher
    from . import build_research_leads as research
    from . import build_shorts_audio_candidates as shorts
    from . import validate_publisher_episode_roster as roster
else:
    import build_film_catalog as films
    import build_literary_candidates as literature
    import build_legacy_s1_discovery as legacy1
    import build_legacy_s2_discovery as legacy
    import build_legacy_s3_discovery as legacy3
    import build_prodigy_publisher_discovery as prodigy
    import build_publisher_s4_discovery as season4
    import build_publisher_s5_discovery as season5
    import build_publisher_s6_discovery as season6
    import build_publisher_s7_discovery as season7
    import build_tas_publisher_roster as tas
    import build_prodigy_mikros_s1a_discovery as mikros
    import build_scouts_publisher_discovery as scouts
    import build_publisher_catalog as publisher
    import build_research_leads as research
    import build_shorts_audio_candidates as shorts
    import validate_publisher_episode_roster as roster


OUTPUT = Path("explorer/discovery-catalog.json")
INPUTS = (
    Path("explorer/film-catalog.json"),
    Path("explorer/research-leads.json"),
    Path("proposals/discovery/publisher-catalog.json"),
    Path("proposals/librarian/ring-of-fire-editions-20261102/records.json"),
)
EPISODES = Path("proposals/discovery/ds9-voy-episode-slots-20261102")
ROSTER_BATCHES = (
    (EPISODES, ("ds9", "voy", "tas"), "roster", 15),
    (Path("proposals/discovery/modern-paramount-season1-20261102"),
     ("dis", "pic", "ld", "snw"), "modern-s1", 45),
    (Path("proposals/discovery/modern-paramount-season2-first5-20261102"),
     ("dis", "pic", "ld", "snw"), "modern-s2", 20),
    (Path("proposals/discovery/modern-paramount-season3-20261102"),
     ("dis", "pic", "ld", "snw"), "modern-s3", 43),
)
SHORTS_INPUT = Path("proposals/discovery/shorts-audio-20261102/records.json")
SCOUTS_INPUT = scouts.OUTPUT
MEDIUMS = ("EPISODE", "FILM", "LITERATURE", "SHORT_FORM", "AUDIO")
KINDS = ("WIKIDATA_EPISODE", "PUBLISHER_EPISODE_SLOT", "PUBLISHER_REFERENCE",
         "FEATURE_FILM", "STREAMING_FILM", "NOVEL", "SCRIPTED_SHORT",
         "PROMOTIONAL_ANIMATION", "SCRIPTED_AUDIO_SERIES")
ALLOWED_HOSTS = {"www.wikidata.org", "www.startrek.com", "www.paramountplus.com",
                 "www.simonandschuster.com", "www.mikrosanimation.com", "youtu.be"}


def _checked_title(value: object) -> str:
    if (not isinstance(value, str) or not 1 <= len(value) <= 200 or
            value != value.strip() or any(ord(char) < 32 for char in value)):
        raise ValueError("invalid discovery display title")
    return value


def _checked_url(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("discovery locator must be a URL or null")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc not in ALLOWED_HOSTS or
            parsed.username or parsed.password or parsed.query or parsed.fragment or
            not parsed.path.startswith("/") or ".." in parsed.path):
        raise ValueError("discovery locator outside approved source domains")
    if parsed.netloc == "youtu.be" and not re.fullmatch(r"/[A-Za-z0-9_-]{11}", parsed.path):
        raise ValueError("source-local YouTube video locator must have an exact video ID")
    return value


def _document(root: Path, path: Path, expected: bytes | None = None) -> tuple[dict, str]:
    raw = research.safe_read(root, path, max_bytes=1_500_000)
    if expected is not None and raw != expected:
        raise ValueError(f"stale discovery source derivative: {path}")
    data = research._strict_json(raw, str(path))
    if not isinstance(data, dict):
        raise ValueError(f"discovery source must be an object: {path}")
    return data, hashlib.sha256(raw).hexdigest()


def _row(ident: str, medium: str, kind: str, title: str, context: str,
         group: str, origin: str, locator: str | None, details: tuple[str, ...] = ()) -> dict:
    if not re.fullmatch(r"[a-z0-9:_.-]{3,210}", ident) or medium not in MEDIUMS or kind not in KINDS:
        raise ValueError("invalid discovery local identifier or kind")
    if not isinstance(group, str) or not 3 <= len(group) <= 120:
        raise ValueError("invalid source lineage")
    if not isinstance(context, str) or not 1 <= len(context) <= 160:
        raise ValueError("invalid display context")
    if len(details) > 8 or any(not isinstance(d, str) or len(d) > 150 for d in details):
        raise ValueError("invalid discovery detail list")
    return {
        "row_id": ident, "medium": medium, "candidate_kind": kind,
        "title": _checked_title(title), "context": context,
        "source_group": group, "source_input": origin,
        "source_locator": _checked_url(locator), "details": list(details),
        "verification_status": "UNVERIFIED_METADATA", "identity_scope": "SOURCE_LOCAL",
        "coverage_effect": "NONE", "admission_effect": "NONE",
    }


def build_bytes(root: Path) -> bytes:
    sources = {}
    for path, builder in (
        (INPUTS[0], films.build(root)),
        (INPUTS[1], research.build_bytes(root)),
        (INPUTS[2], publisher.build_bytes(root)),
        (INPUTS[3], literature.build(root)),
        (SHORTS_INPUT, shorts.build(root)),
        (SCOUTS_INPUT, scouts.build(root)),
    ):
        value, digest = _document(root, path, builder)
        sources[str(path)] = digest
        if str(path) == str(INPUTS[0]): film_catalog = value
        if str(path) == str(INPUTS[1]): leads_catalog = value
        if str(path) == str(INPUTS[2]): publisher_catalog = value
        if str(path) == str(INPUTS[3]): novel_catalog = value
        if path == SHORTS_INPUT: shorts_catalog = value
        if path == SCOUTS_INPUT: scouts_catalog = value

    if (film_catalog.get("data_status") != "DISCOVERY_ONLY" or
            film_catalog.get("coverage_effect") != "NONE" or
            film_catalog.get("film_count") != len(film_catalog.get("films", []))):
        raise ValueError("film metadata not discovery-only")
    if (leads_catalog.get("data_status") != "CANDIDATE_DISCOVERY_ONLY" or
            leads_catalog.get("coverage_effect") != "NONE" or
            leads_catalog.get("lead_count") != len(leads_catalog.get("leads", []))):
        raise ValueError("research leads not discovery-only")
    if (publisher_catalog.get("status") != "UNVERIFIED_PUBLISHER_DISCOVERY_ONLY" or
            publisher_catalog.get("candidate_row_count") != len(publisher_catalog.get("rows", []))):
        raise ValueError("publisher sidecar not discovery-only")
    if (novel_catalog.get("proposal_only") is not True or
            novel_catalog.get("coverage_effect") != "NONE" or
            novel_catalog.get("accepted_work_effect") != "NONE"):
        raise ValueError("literary work not proposal-only")

    entries = []
    for idx, lead in enumerate(leads_catalog["leads"]):
        kind = lead["source_type"]
        if kind not in ("WIKIDATA_METADATA", "PUBLISHER_EPISODE_SLOT_METADATA"):
            raise ValueError("unexpected episode lead lineage")
        locator = ("https://www.wikidata.org/wiki/" + lead["episode_qid"]
                   if kind == "WIKIDATA_METADATA" else lead["source_locator"])
        source = "WIKIDATA_EPISODE" if kind == "WIKIDATA_METADATA" else "PUBLISHER_EPISODE_SLOT"
        slot = (f" S{lead['season_number']}E{lead['episode_number']}"
                if kind != "WIKIDATA_METADATA" else "")
        entries.append(_row(f"lead:{idx:04d}", "EPISODE", source,
                            lead["episode_label"], lead["mission_id"].upper() + slot,
                            lead["independence_group"], str(INPUTS[1]), locator))

    for idx, source in enumerate(publisher_catalog["rows"]):
        episode = (f" S{source['season_number']}E{source['episode_number']}"
                   if source["episode_number"] is not None else " · episode unresolved")
        entries.append(_row(f"publisher:{idx:04d}", "EPISODE", "PUBLISHER_REFERENCE",
                            source["proposed_title"], source["mission_id"].upper() + episode,
                            source["independence_group"], str(INPUTS[2]), source["source_locator"]))

    catalog = research._strict_json(research.safe_read(root, Path("registry/mission_catalog.json")), "mission catalog")
    for folder, missions, batch_id, expected in ROSTER_BATCHES:
        added = 0
        for mission in missions:
            bundle_path = folder / mission / "bundle.json"
            csv_path = folder / f"{mission}-observed-slots.csv"
            receipt_path = folder / f"{mission}-observation.json"
            bundle, bundle_digest = _document(root, bundle_path)
            receipt, receipt_digest = _document(root, receipt_path)
            raw = research.safe_read(root, csv_path, max_bytes=128_000)
            if hashlib.sha256(raw).hexdigest() != receipt.get("csv_sha256"):
                raise ValueError("publisher observation CSV digest mismatch")
            source_rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
            if (not source_rows or len(source_rows) != len(bundle.get("episode_slots", [])) or
                    any(set(item) != {"season", "episode_number", "title"} for item in source_rows)):
                raise ValueError("publisher slot receipt shape mismatch")
            roster.validate(bundle, catalog)
            for idx, (observed, slot) in enumerate(zip(source_rows, bundle["episode_slots"])):
                if (int(observed["season"]) != slot["season"] or
                        int(observed["episode_number"]) != slot["episode_number"] or
                        observed["title"] != slot["title"]):
                    raise ValueError("publisher slot CSV and bundle disagree")
                ident = (f"roster:{mission}:{idx:03d}" if batch_id == "roster" else
                         f"roster:{batch_id}:{mission}:{idx:03d}")
                entries.append(_row(ident, "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                    slot["title"], f"{mission.upper()} S{slot['season']}E{slot['episode_number']}",
                                    bundle["observation"]["independence_group"], str(bundle_path),
                                    bundle["observation"]["primary_locator"]))
                added += 1
            sources[str(bundle_path)] = bundle_digest
            sources[str(receipt_path)] = receipt_digest
            sources[str(csv_path)] = hashlib.sha256(raw).hexdigest()
        if added != expected:
            raise ValueError(f"unexpected reviewed episode source-row count in {batch_id}")

    # Each publisher season is a separate source-observation batch. Preserve
    # repeated titles/identities between seasons and other source families.
    for builder, season_number, expected_count in ((legacy1, 1, 114), (legacy, 2, 126), (legacy3, 3, 126)):
        legacy_index_path = builder.BASE / "index.json"
        legacy_index, legacy_digest = _document(root, legacy_index_path)
        sources[str(legacy_index_path)] = legacy_digest
        if (legacy_index.get("proposal_status") != "DISCOVERY_ONLY" or
                legacy_index.get("admission_effect") != "NONE" or
                legacy_index.get("coverage_effect") != "NONE" or
                legacy_index.get("denominator_effect") != "NONE" or
                legacy_index.get("publisher") != "Paramount+" or
                legacy_index.get("independence_group") != "publisher:paramount" or
                len(legacy_index.get("source_pages", [])) != len(builder.SLUGS)):
            raise ValueError("legacy source observations not bounded candidate-only")
        legacy_count = 0
        for mission, page in zip(builder.SLUGS, legacy_index["source_pages"]):
            if (page.get("mission_id") != mission or
                    page.get("official_page") != builder.official_url(mission) or
                    not re.fullmatch(r"[a-f0-9]{64}", str(page.get("source_body_sha256"))) or
                    type(page.get("source_body_bytes")) is not int or
                    not 10_000 <= page["source_body_bytes"] <= 3_000_000):
                raise ValueError("legacy page source receipt not pinned to official episode listing")
            csv_path = builder.BASE / f"{mission}.csv"
            bundle_path = builder.BASE / mission / "bundle.json"
            csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
            if hashlib.sha256(csv_raw).hexdigest() != page.get("observation_csv_sha256"):
                raise ValueError("legacy CSV observation digest mismatch")
            rows = builder.parse_csv(csv_raw)
            bundle, bundle_digest = _document(root, bundle_path, builder.serialized(builder.bundle(mission, rows)))
            roster.validate(bundle, catalog)
            if page.get("listed_slot_count") != len(rows) or bundle["listed_slot_count"] != len(rows):
                raise ValueError("legacy listed episode count inconsistent")
            if bundle["observation"]["primary_locator"] != page["official_page"]:
                raise ValueError("legacy bundle locator disagrees with source receipt")
            for idx, (season, episode, title) in enumerate(rows):
                entries.append(_row(f"legacy:s{season_number}:{mission}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                    title, f"{mission.upper()} S{season}E{episode}",
                                    legacy_index["independence_group"], str(bundle_path),
                                    page["official_page"], (f"Official publisher season-{season_number} listing",)))
                legacy_count += 1
            sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
            sources[str(bundle_path)] = bundle_digest
        if legacy_count != expected_count:
            raise ValueError(f"legacy season-{season_number} changed from reviewed {expected_count} source-local listings")

    # The official StarTrek.com Prodigy observations are separate publisher
    # title-list sources. Season 1 episode slots 1–10 are deliberately absent:
    # no matching numbered primary publisher list was evidenced in this batch.
    prodigy_index_path = prodigy.BASE / "index.json"
    prodigy_index, prodigy_digest = _document(root, prodigy_index_path)
    sources[str(prodigy_index_path)] = prodigy_digest
    if (prodigy_index.get("proposal_status") != "DISCOVERY_ONLY" or
            prodigy_index.get("admission_effect") != "NONE" or
            prodigy_index.get("coverage_effect") != "NONE" or
            prodigy_index.get("denominator_effect") != "NONE" or
            prodigy_index.get("publisher") != "StarTrek.com" or
            prodigy_index.get("independence_group") != "publisher:paramount" or
            prodigy_index.get("acknowledged_gaps") != prodigy.index([])["acknowledged_gaps"] or
            len(prodigy_index.get("source_pages", [])) != len(prodigy.SOURCES)):
        raise ValueError("Prodigy source observations not bounded candidate-only")
    prodigy_count = 0
    for spec, page in zip(prodigy.SOURCES, prodigy_index["source_pages"]):
        source_id, official_url, season_number, first, last = spec
        if (not isinstance(page, dict) or set(page) != prodigy.RECEIPT_KEYS or
                page.get("source_id") != source_id or
                page.get("official_page") != official_url or
                page.get("season") != season_number or
                page.get("observed_episode_range") != [first, last] or
                not re.fullmatch(r"[0-9a-f]{64}", str(page.get("source_body_sha256"))) or
                type(page.get("source_body_bytes")) is not int or
                not 100_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("Prodigy source receipt does not match publisher listing")
        csv_path = prodigy.BASE / f"{source_id}.csv"
        bundle_path = prodigy.BASE / source_id / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page.get("observation_csv_sha256"):
            raise ValueError("Prodigy publisher observation CSV digest mismatch")
        rows = prodigy.read_csv(csv_raw, source_id)
        bundle, bundle_digest = _document(
            root, bundle_path, prodigy.serialize(prodigy.candidate_bundle(source_id, rows)))
        roster.validate(bundle, catalog)
        if (page.get("listed_slot_count") != len(rows) or
                bundle.get("listed_slot_count") != len(rows) or
                bundle["observation"]["primary_locator"] != official_url):
            raise ValueError("Prodigy source and source-local bundle disagree")
        for idx, (season, episode, title) in enumerate(rows):
            entries.append(_row(f"prodigy:{source_id}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"PRO S{season}E{episode}",
                                prodigy_index["independence_group"], str(bundle_path),
                                official_url, (f"Official publisher {source_id} listing",)))
            prodigy_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if prodigy_count != 30:
        raise ValueError(f"Prodigy publisher source-local observations changed from 30: {prodigy_count}")

    # Six season-four publisher guides are a single new candidate-only batch.
    # Slot numbering is source-relative; absent multipart ordinals are NOT
    # invented, and repeated episode appearances remain separate observations.
    season4_index_path = season4.BASE / "index.json"
    season4_index, season4_digest = _document(root, season4_index_path)
    sources[str(season4_index_path)] = season4_digest
    expected_by_mission = {"tng": 26, "ds9": 25, "voy": 26, "ent": 22, "dis": 13, "ld": 10}
    if (set(season4_index) != season4.INDEX_KEYS or
            {key: season4_index[key] for key in season4.INDEX_KEYS - {"source_pages"}}
            != {key: season4.source_index([])[key] for key in season4.INDEX_KEYS - {"source_pages"}} or
            not isinstance(season4_index.get("source_pages"), list) or
            len(season4_index["source_pages"]) != len(season4.SLUGS)):
        raise ValueError("Season 4 source index is not bounded candidate-only metadata")
    season4_count = 0
    for mission, page in zip(season4.SLUGS, season4_index["source_pages"]):
        if (not isinstance(page, dict) or set(page) != season4.PAGE_KEYS or
                page["mission_id"] != mission or
                page["official_page"] != season4.official_url(mission) or
                not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("Season 4 publisher page receipt invalid or misbound")
        csv_path = season4.BASE / f"{mission}.csv"
        bundle_path = season4.BASE / mission / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page["observation_csv_sha256"]:
            raise ValueError("Season 4 source CSV receipt digest mismatch")
        rows = season4.parse_csv(csv_raw)
        bundle, bundle_digest = _document(
            root, bundle_path, season4.source_tools.serialized(season4.bundle(mission, rows)))
        roster.validate(bundle, catalog)
        if (len(rows) != expected_by_mission[mission] or
                page["listed_slot_count"] != len(rows) or
                bundle["listed_slot_count"] != len(rows) or
                bundle["observation"]["primary_locator"] != page["official_page"]):
            raise ValueError("Season 4 publisher CSV, source or bundle changed")
        for idx, (season, episode, title) in enumerate(rows):
            entries.append(_row(f"publisher:s4:{mission}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"{mission.upper()} S{season}E{episode}",
                                season4_index["independence_group"], str(bundle_path),
                                page["official_page"], ("Official publisher season-4 listing",)))
            season4_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if season4_count != 122:
        raise ValueError(f"Season 4 publisher observation count changed from reviewed 122: {season4_count}")

    # Season 5 forms an additional source-local publisher tranche, not a
    # deduplicated episode count or a canonical Work reconciliation. Voyager's
    # absent publisher ordinal S5E16 is left absent, never synthesized.
    season5_index_path = season5.BASE / "index.json"
    season5_index, season5_digest = _document(root, season5_index_path)
    sources[str(season5_index_path)] = season5_digest
    expected_s5 = {"tng": 26, "ds9": 26, "voy": 25, "dis": 10, "ld": 10}
    if (set(season5_index) != season5.INDEX_KEYS or
            {key: season5_index[key] for key in season5.INDEX_KEYS - {"source_pages"}}
            != {key: season5.source_index([])[key] for key in season5.INDEX_KEYS - {"source_pages"}} or
            not isinstance(season5_index.get("source_pages"), list) or
            len(season5_index["source_pages"]) != len(season5.SLUGS)):
        raise ValueError("Season 5 source index is not bounded candidate-only metadata")
    season5_count = 0
    for mission, page in zip(season5.SLUGS, season5_index["source_pages"]):
        if (not isinstance(page, dict) or set(page) != season5.PAGE_KEYS or
                page["mission_id"] != mission or
                page["official_page"] != season5.official_url(mission) or
                not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("Season 5 publisher page receipt invalid or misbound")
        csv_path = season5.BASE / f"{mission}.csv"
        bundle_path = season5.BASE / mission / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page["observation_csv_sha256"]:
            raise ValueError("Season 5 source CSV receipt digest mismatch")
        rows = season5.parse_csv(csv_raw)
        bundle, bundle_digest = _document(
            root, bundle_path, season5.source_tools.serialized(season5.bundle(mission, rows)))
        roster.validate(bundle, catalog)
        if (len(rows) != expected_s5[mission] or
                page["listed_slot_count"] != len(rows) or
                bundle["listed_slot_count"] != len(rows) or
                bundle["observation"]["primary_locator"] != page["official_page"]):
            raise ValueError("Season 5 publisher CSV, source or bundle changed")
        for idx, (season, episode, title) in enumerate(rows):
            entries.append(_row(f"publisher:s5:{mission}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"{mission.upper()} S{season}E{episode}",
                                season5_index["independence_group"], str(bundle_path),
                                page["official_page"], ("Official publisher season-5 listing",)))
            season5_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if season5_count != 97:
        raise ValueError(f"Season 5 publisher observation count changed from reviewed 97: {season5_count}")

    # Three official Season 6 guides provide independent *rows*, not
    # independent corroboration: Paramount remains one provenance family.
    # Every publisher ordinal is kept source-local and non-admitted.
    season6_index_path = season6.BASE / "index.json"
    season6_index, season6_digest = _document(root, season6_index_path)
    sources[str(season6_index_path)] = season6_digest
    expected_s6 = {"tng": 26, "ds9": 26, "voy": 26}
    if (set(season6_index) != season6.INDEX_KEYS or
            {key: season6_index[key] for key in season6.INDEX_KEYS - {"source_pages"}}
            != {key: season6.source_index([])[key] for key in season6.INDEX_KEYS - {"source_pages"}} or
            not isinstance(season6_index.get("source_pages"), list) or
            len(season6_index["source_pages"]) != len(season6.SLUGS)):
        raise ValueError("Season 6 source index is not bounded candidate-only metadata")
    season6_count = 0
    for mission, page in zip(season6.SLUGS, season6_index["source_pages"]):
        if (not isinstance(page, dict) or set(page) != season6.PAGE_KEYS or
                page["mission_id"] != mission or
                page["official_page"] != season6.official_url(mission) or
                not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("Season 6 publisher page receipt invalid or misbound")
        csv_path = season6.BASE / f"{mission}.csv"
        bundle_path = season6.BASE / mission / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page["observation_csv_sha256"]:
            raise ValueError("Season 6 source CSV receipt digest mismatch")
        rows = season6.parse_csv(csv_raw)
        bundle, bundle_digest = _document(
            root, bundle_path, season6.source_tools.serialized(season6.bundle(mission, rows)))
        roster.validate(bundle, catalog)
        if (len(rows) != expected_s6[mission] or
                page["listed_slot_count"] != len(rows) or
                bundle["listed_slot_count"] != len(rows) or
                bundle["observation"]["primary_locator"] != page["official_page"]):
            raise ValueError("Season 6 publisher CSV, source or bundle changed")
        for idx, (season, episode, title) in enumerate(rows):
            entries.append(_row(f"publisher:s6:{mission}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"{mission.upper()} S{season}E{episode}",
                                season6_index["independence_group"], str(bundle_path),
                                page["official_page"], ("Official publisher season-6 listing",)))
            season6_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if season6_count != 78:
        raise ValueError(f"Season 6 publisher observation count changed from reviewed 78: {season6_count}")

    # The three Season 7 guides are candidate metadata, not a canonical
    # season/Work census. The Voyager publisher omits S7E10; preserve that
    # source gap and do not create a synthetic episode observation.
    season7_index_path = season7.BASE / "index.json"
    season7_index, season7_digest = _document(root, season7_index_path)
    sources[str(season7_index_path)] = season7_digest
    expected_s7 = {"tng": 25, "ds9": 25, "voy": 24}
    if (set(season7_index) != season7.INDEX_KEYS or
            {key: season7_index[key] for key in season7.INDEX_KEYS - {"source_pages"}}
            != {key: season7.source_index([])[key] for key in season7.INDEX_KEYS - {"source_pages"}} or
            not isinstance(season7_index.get("source_pages"), list) or
            len(season7_index["source_pages"]) != len(season7.SLUGS)):
        raise ValueError("Season 7 source index is not bounded candidate-only metadata")
    season7_count = 0
    for mission, page in zip(season7.SLUGS, season7_index["source_pages"]):
        if (not isinstance(page, dict) or set(page) != season7.PAGE_KEYS or
                page["mission_id"] != mission or
                page["official_page"] != season7.official_url(mission) or
                not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("Season 7 publisher page receipt invalid or misbound")
        csv_path = season7.BASE / f"{mission}.csv"
        bundle_path = season7.BASE / mission / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page["observation_csv_sha256"]:
            raise ValueError("Season 7 source CSV receipt digest mismatch")
        rows = season7.parse_csv(csv_raw)
        bundle, bundle_digest = _document(
            root, bundle_path, season7.source_tools.serialized(season7.bundle(mission, rows)))
        roster.validate(bundle, catalog)
        if (len(rows) != expected_s7[mission] or
                page["listed_slot_count"] != len(rows) or
                bundle["listed_slot_count"] != len(rows) or
                bundle["observation"]["primary_locator"] != page["official_page"]):
            raise ValueError("Season 7 publisher CSV, source or bundle changed")
        for idx, (season, episode, title) in enumerate(rows):
            entries.append(_row(f"publisher:s7:{mission}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"{mission.upper()} S{season}E{episode}",
                                season7_index["independence_group"], str(bundle_path),
                                page["official_page"], ("Official publisher season-7 listing",)))
            season7_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if season7_count != 74:
        raise ValueError(f"Season 7 publisher observation count changed from reviewed 74: {season7_count}")

    # TAS publisher Seasons 1 and 2 are independent *source-local snapshots*
    # of season guides. Five S1 titles/slots overlap an older TAS roster;
    # compiling 22 rows does not reconcile them or admit 22 new Works.
    tas_index_path = tas.BASE / "index.json"
    tas_index, tas_digest = _document(root, tas_index_path)
    sources[str(tas_index_path)] = tas_digest
    if (set(tas_index) != tas.safe.INDEX_KEYS or
            {key: tas_index[key] for key in tas.safe.INDEX_KEYS - {"source_pages"}}
            != {key: tas.source_index([])[key] for key in tas.safe.INDEX_KEYS - {"source_pages"}} or
            not isinstance(tas_index.get("source_pages"), list) or
            len(tas_index["source_pages"]) != len(tas.SEASONS)):
        raise ValueError("TAS season source index is not bounded candidate metadata")
    tas_count = 0
    for season, page in zip(tas.SEASONS, tas_index["source_pages"]):
        if (not isinstance(page, dict) or set(page) != tas.safe.PAGE_KEYS or
                page["mission_id"] != "tas" or
                page["official_page"] != tas.official_url(season) or
                not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("TAS source receipt invalid or misbound")
        csv_path = tas.BASE / f"s{season}.csv"
        bundle_path = tas.BASE / f"s{season}" / "bundle.json"
        csv_raw = research.safe_read(root, csv_path, max_bytes=16_384)
        if hashlib.sha256(csv_raw).hexdigest() != page["observation_csv_sha256"]:
            raise ValueError("TAS CSV source receipt mismatch")
        rows = tas.parse_csv(csv_raw, season)
        bundle, bundle_digest = _document(root, bundle_path, tas.source.serialized(tas.bundle(season, rows)))
        roster.validate(bundle, catalog)
        if (len(rows) != (16 if season == 1 else 6) or
                page["listed_slot_count"] != len(rows) or
                bundle["listed_slot_count"] != len(rows) or
                bundle["observation"]["primary_locator"] != page["official_page"]):
            raise ValueError("TAS source observations changed from reviewed season listing")
        for idx, (_, episode, title) in enumerate(rows):
            entries.append(_row(f"publisher:tas:s{season}:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                                title, f"TAS S{season}E{episode}", tas_index["independence_group"],
                                str(bundle_path), page["official_page"],
                                ("Publisher source-local roster; overlapping earlier observations possible",)))
            tas_count += 1
        sources[str(csv_path)] = hashlib.sha256(csv_raw).hexdigest()
        sources[str(bundle_path)] = bundle_digest
    if tas_count != 22:
        raise ValueError("TAS publisher source-local roster changed from reviewed 22")

    # A Mikros Animation first-volume article gives ten titles in prose, not
    # a numbered title guide. Sequence positions are explicitly *inferred*.
    # Its isolated Starstruck 'Ep#103' image-caption label is retained without
    # extending that observation into a numbered roster or corroboration.
    mikros_index_path = mikros.BASE / "index.json"
    mikros_index, mikros_digest = _document(root, mikros_index_path)
    sources[str(mikros_index_path)] = mikros_digest
    if (set(mikros_index) != mikros.SOURCE_KEYS or
            any(mikros_index.get(k) != v for k, v in {
                "schema_version": "1.0.0", "batch_id": "prodigy-mikros-volume1-20261102",
                "proposal_status": "CANDIDATE_METADATA_ONLY", "source_id": mikros.SOURCE_ID,
                "publisher": "Mikros Animation", "independence_group": "publisher:paramount",
                "source_page": mikros.URL, "listed_title_count": 10,
                "ordinal_basis": "INFERRED_FROM_STUDIO_VOLUME_1_FIRST_TEN_LISTED_ORDER_NOT_NUMBERED",
                "crosscheck_locator": mikros.CROSSCHECK,
                "crosscheck_limit": "FIRST_TEN_VOLUME_EXISTENCE_ONLY_NO_TITLE_OR_ORDINAL_ROSTER",
                "admission_effect": "NONE", "coverage_effect": "NONE",
            }.items()) or
            mikros_index.get("title_expansions") != ["slot_2_contextual_part_ii", "slot_10_contextual_part_2"] or
            mikros_index.get("caption_exception") != {
                "title": "Starstruck", "literal_label": "Ep#103",
                "origin": "SAME_MIKROS_ARTICLE_FIGCAPTION",
                "season_ordinal_or_independence_effect": "NONE",
            } or
            not re.fullmatch(r"[0-9a-f]{64}", str(mikros_index.get("raw_sha256"))) or
            type(mikros_index.get("raw_bytes")) is not int or
            not 10_000 <= mikros_index["raw_bytes"] <= 500_000):
        raise ValueError("Mikros source receipt, caption exception or inference boundary invalid")
    mikros_csv_path = mikros.BASE / f"{mikros.SOURCE_ID}.csv"
    mikros_bundle_path = mikros.BASE / mikros.SOURCE_ID / "bundle.json"
    mikros_raw = research.safe_read(root, mikros_csv_path, max_bytes=10_000)
    if hashlib.sha256(mikros_raw).hexdigest() != mikros_index.get("csv_sha256"):
        raise ValueError("Mikros CSV source receipt mismatch")
    mikros_rows = mikros.read_csv(mikros_raw)
    mikros_bundle, mikros_bundle_digest = _document(
        root, mikros_bundle_path, mikros.serialize(mikros.bundle(mikros_rows)))
    roster.validate(mikros_bundle, catalog)
    if mikros_bundle["listed_slot_count"] != 10 or mikros_bundle["observation"]["primary_locator"] != mikros.URL:
        raise ValueError("Mikros source-local title-list bundle changed")
    for idx, (_, positional_index, title) in enumerate(mikros_rows):
        entries.append(_row(f"studio:mikros-s1a:{idx:03d}", "EPISODE", "PUBLISHER_EPISODE_SLOT",
                            title, f"PRO S1 title-list position {positional_index} (inferred)",
                            mikros_index["independence_group"], str(mikros_bundle_path), mikros.URL,
                            ("Volume 1 first-ten title-list order; ordinal not publisher-numbered",
                             "Starstruck photo caption: Ep#103 (same source)" if title == "Starstruck"
                             else "No separately observed per-title ordinal label")))
    sources[str(mikros_csv_path)] = hashlib.sha256(mikros_raw).hexdigest()
    sources[str(mikros_bundle_path)] = mikros_bundle_digest

    if (shorts_catalog.get("data_status") != "DISCOVERY_ONLY" or
            shorts_catalog.get("admission_effect") != "NONE" or
            shorts_catalog.get("coverage_effect") != "NONE" or
            shorts_catalog.get("universe_complete") is not False or
            shorts_catalog.get("short_candidate_count") != 15 or
            shorts_catalog.get("container_count") != 3):
        raise ValueError("short-form metadata not discovery-only")
    for item in shorts_catalog["short_candidates"]:
        kind = ("SCRIPTED_SHORT" if item["parent_candidate_id"] == "short-treks"
                else "PROMOTIONAL_ANIMATION" if item["parent_candidate_id"] == "very-short-treks"
                else None)
        if kind is None or item["verification_status"] != "UNVERIFIED_METADATA":
            raise ValueError("unexpected short-form episode promotion")
        entries.append(_row("short:" + item["candidate_id"], "SHORT_FORM", kind,
                            item["title"], item["parent_candidate_id"] + " · " + item["source_local_slot"],
                            shorts_catalog["publisher_independence_group"], str(SHORTS_INPUT),
                            item["source_url"], ("Official episode slot" if kind == "SCRIPTED_SHORT"
                                                  else "Announced promotional release order",)))
    # The new publisher's official twenty short videos have two #1-#10
    # strands, not verified global television season ordinals. Preserve the
    # title/URL lineage and explicit no-admission boundary.
    if (scouts_catalog.get("schema_version") != "1.0.0" or
            scouts_catalog.get("data_status") != "DISCOVERY_ONLY" or
            scouts_catalog.get("admission_effect") != "NONE" or
            scouts_catalog.get("coverage_effect") != "NONE" or
            scouts_catalog.get("publisher_independence_group") != "publisher:paramount" or
            scouts_catalog.get("source_input") != str(scouts.SOURCE) or
            scouts_catalog.get("short_candidate_count") != 20 or
            len(scouts_catalog.get("short_candidates", [])) != 20):
        raise ValueError("Scouts discovery source changed its no-admission boundary")
    for item in scouts_catalog["short_candidates"]:
        if (item.get("verification_status") != "UNVERIFIED_METADATA" or
                item.get("accepted_work_id", "unexpected") is not None):
            raise ValueError("Scouts candidate illegally promoted to an accepted Work")
        entries.append(_row("short:" + item["candidate_id"], "SHORT_FORM", "SCRIPTED_SHORT",
                            item["title"], "SCOUTS · " + item["strand"].replace("_", " ") +
                            " " + item["source_local_slot"],
                            scouts_catalog["publisher_independence_group"], str(SCOUTS_INPUT),
                            item["source_locator"], ("Publisher video title; video not watched",
                                                    "Source-local strand number, not global season ordinal")))
    sources[str(scouts.SOURCE)] = hashlib.sha256(research.safe_read(root, scouts.SOURCE,
                                                                max_bytes=35_000)).hexdigest()
    audio = [item for item in shorts_catalog["container_candidates"] if item["medium"] == "SCRIPTED_AUDIO"]
    if (len(audio) != 1 or audio[0]["candidate_id"] != "khan-audio" or
            audio[0]["work_type"] != "SCRIPTED_AUDIO_SERIES" or
            audio[0]["verification_status"] != "UNVERIFIED_METADATA"):
        raise ValueError("scripted-audio container is not a single source-local candidate")
    audio_source = {source["id"]: source for source in shorts_catalog["sources"]}[audio[0]["source_id"]]
    entries.append(_row("audio:" + audio[0]["candidate_id"], "AUDIO", "SCRIPTED_AUDIO_SERIES",
                        audio[0]["title"], "Scripted audio-series container · zero admitted episodes",
                        shorts_catalog["publisher_independence_group"], str(SHORTS_INPUT),
                        audio_source["url"]))

    for film in film_catalog["films"]:
        kind = "STREAMING_FILM" if film["work_type"] == "STREAMING_ORIGINAL_FILM" else "FEATURE_FILM"
        entries.append(_row("film:" + film["id"], "FILM", kind, film["title"],
                            "Star Trek films", film["source_group"], str(INPUTS[0]), film["source_locator"]))

    work = novel_catalog["work"]
    editions = novel_catalog["edition_candidates"]
    if len(novel_catalog["sources"]) != len(editions) or len(editions) != 4:
        raise ValueError("literary edition count inconsistent")
    source_by_id = {source["source_id"]: source for source in novel_catalog["sources"]}
    if len(source_by_id) != len(editions):
        raise ValueError("literary source identifiers duplicated")
    details = tuple(f"{item['format'].replace('_', ' ').title()} · ISBN {item['isbn13']}"
                    for item in editions)
    for edition in editions:
        if edition["work_id"] != work["work_id"] or edition["source_id"] not in source_by_id:
            raise ValueError("literary source edition binding unresolved")
    entries.append(_row("literature:" + work["work_id"], "LITERATURE", "NOVEL",
                        work["title"], f"{work['creator']} · {len(editions)} publisher editions",
                        novel_catalog["source_group"], str(INPUTS[3]),
                        source_by_id[editions[0]["source_id"]]["locator"], details))

    identities = [r["row_id"] for r in entries]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate source-local index identifier")
    counts = {medium: sum(row["medium"] == medium for row in entries) for medium in MEDIUMS}
    output = {
        "schema_version": "1.0.0", "data_status": "DISCOVERY_ONLY",
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "denominator_status": "NOT_ESTABLISHED", "identity_scope": "SOURCE_LOCAL_NOT_DEDUPLICATED",
        "row_count": len(entries), "counts_by_medium": counts,
        "source_digests": [{"path": path, "sha256": digest} for path, digest in sorted(sources.items())],
        "rows": entries,
    }
    return (json.dumps(output, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        blob = build_bytes(args.repo_root)
        if args.check:
            existing = research.safe_read(args.repo_root, OUTPUT, max_bytes=1_500_000)
            if existing != blob:
                raise ValueError("public discovery catalog differs from deterministic source")
        else:
            publisher.safe_write(args.repo_root, OUTPUT, blob)
    except (OSError, ValueError, roster.Rejected, UnicodeError) as exc:
        print(f"PUBLIC_DISCOVERY_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"PUBLIC_DISCOVERY_OK: {len(json.loads(blob)['rows'])} source-local metadata rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
