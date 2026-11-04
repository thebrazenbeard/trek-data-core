#!/usr/bin/env python3
"""Advisory-only, deterministic CC license-version triage; NEVER a public release gate."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/librarian/cc-license-version-held-policy-20261104"
RELEASE_GATE = "tools/validate_artwork_release.py"
RELEASE_GATE_SHA = "402cb3d0620906d8f700bb4335c2e56dea4f7dcb9b396fafc56bef8112d0d35e"
EXPECTED_ALLOWLIST = {"PD-US-no-notice", "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "EXPLICIT_WRITTEN_PERMISSION"}
SOURCE_EXAMPLES = {
    "beyond-premiere-photo-cc-by-2": (
        "explorer/beyond-premiere-photo.json", "bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634",
        "CC-BY-2.0", "CC BY 2.0", "REAL_WORLD_PREMIERE_DOCUMENTARY_PHOTO_NOT_FILM_STILL",
        "HELD_VERSION_CLASS_NOT_ACCEPTED", None, "rights_limit",
    ),
    "lower-decks-sdcc-panel-cc-by-sa-2": (
        "proposals/librarian/lower-decks-sdcc-ccby-sa-source-20261103/record.json",
        "0909ebb6661211ab184d46331d7a7bac9e1789bafba304bc10c232282ac02d10",
        "CC-BY-SA-2.0", "CC_BY_SA_2_0_GENERIC",
        "DOCUMENTARY_CONVENTION_PANEL_NOT_EPISODE_FRAME_STILL_OR_POSTER",
        "HELD_VERSION_CLASS_NOT_ACCEPTED", None, "publicity_mark_limits",
    ),
    "starfleet-rank-derived-insignia-cc-by-sa-4": (
        "proposals/librarian/memory-alpha-artwork-discovery-20261103/records.json",
        "8254d31c262bb68b1988fb16818bade2317785b68163ea7c9726d74f7905476a",
        "CC-BY-SA-4.0", "CC BY-SA 4.0", "POSSIBLE_STARFLEET_RANK_INSIGNIA_NOT_CANONICAL_BRAND_MARK",
        "HELD_FILE_LEVEL_RIGHTS_UNVERIFIED", "commons-starfleet-of1-insignia",
        "underlying_prop_design_and_trademark_status",
    ),
}
LICENSES = {
    "CC-BY-2.0": ("https://creativecommons.org/licenses/by/2.0/legalcode", "2.0", False, False),
    "CC-BY-SA-2.0": ("https://creativecommons.org/licenses/by-sa/2.0/legalcode", "2.0", True, False),
    "CC-BY-4.0": ("https://creativecommons.org/licenses/by/4.0/legalcode", "4.0", False, True),
    "CC-BY-SA-4.0": ("https://creativecommons.org/licenses/by-sa/4.0/legalcode", "4.0", True, True),
}
EXPECTED_ROUTES = {
    "PRESERVE_HELD": ("HELD_NO_CHANGE", ["NONE_BECAUSE_NO_RELEASE_IS_REQUESTED"]),
    "EXACT_FILE_WRITTEN_PERMISSION": (
        "HELD_MISSING_SEPARATELY_REVIEWED_EXACT_FILE_GRANT",
        ["ACTUAL_RIGHTS_HOLDER_AND_EXACT_FILE_GRANT", "INDEPENDENT_RIGHTS_AND_SOURCE_REVIEW",
         "CODE_OWNED_PIN_AND_BYTE_RECEIPT", "OWNER_RELEASE_AUTHORIZATION"]),
    "AUDIT_AND_ADD_EXPLICIT_CC_2_0_SUPPORT": (
        "HELD_PENDING_LICENSE_SPECIFIC_POLICY_AND_TEST_REVIEW",
        ["LEGAL_CODE_VERSION_EXACT_RIGHTS_REVIEW", "EXPLICIT_CODE_AND_RECEIPT_SCHEMA_CHANGE",
         "INDEPENDENT_RIGHTS_AND_SOURCE_REVIEW", "CODE_OWNED_PIN_AND_BYTE_RECEIPT",
         "OWNER_RELEASE_AUTHORIZATION"]),
}


class HeldPolicyRejected(ValueError):
    pass


def _unique(pairs: list[tuple[str, object]]) -> dict:
    d = {}
    for key, value in pairs:
        if key in d:
            raise HeldPolicyRejected(f"duplicate JSON key: {key}")
        d[key] = value
    return d


def _json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 150_000:
        raise HeldPolicyRejected("missing, unsafe or oversized source metadata")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique)


def check_packet_inventory(directory: Path = PACKET) -> None:
    if directory.is_symlink() or not directory.is_dir() or \
            {p.name for p in directory.iterdir()} != {"records.json", "MANIFEST.md"}:
        raise HeldPolicyRejected("metadata-only packet inventory changed")
    for file in directory.iterdir():
        if file.is_symlink() or not file.is_file() or file.stat().st_size > 100_000:
            raise HeldPolicyRejected("unsafe packet file")
        data = file.read_bytes()
        if b"\x00" in data or data.startswith((b"\xff\xd8", b"\x89PNG", b"GIF89", b"%PDF")):
            raise HeldPolicyRejected("binary data disguised as policy text")
        text = data.decode("utf-8", errors="strict")
        if re.search(r"<\s*(?:img|svg|iframe|picture|source|video|audio)\b|!\[|data:image/", text, re.I):
            raise HeldPolicyRejected("embedded public/media reference in policy packet")


def _match(given: object, expected: object, label: str) -> None:
    if type(given) is not type(expected) or given != expected:
        raise HeldPolicyRejected(f"held policy/evidence drift: {label}")


def _release_bases(root: Path) -> set[str]:
    path = root / RELEASE_GATE
    if hashlib.sha256(path.read_bytes()).hexdigest() != RELEASE_GATE_SHA:
        raise HeldPolicyRejected("accepted artwork release gate SHA drift")
    syntax = ast.parse(path.read_text(encoding="utf-8"))
    matches = [node for node in syntax.body if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == "LICENSE_BASES" for target in node.targets)]
    if len(matches) != 1:
        raise HeldPolicyRejected("release gate license allowlist absent or ambiguous")
    value = ast.literal_eval(matches[0].value)
    if not isinstance(value, set) or value != EXPECTED_ALLOWLIST:
        raise HeldPolicyRejected("release gate license allowlist drift")
    pin_assigns = [node for node in syntax.body if isinstance(node, ast.AnnAssign)
                   and isinstance(node.target, ast.Name) and node.target.id == "REVIEWED_LOCAL_ARTWORK_PINS"]
    if len(pin_assigns) != 1 or ast.literal_eval(pin_assigns[0].value) != {}:
        raise HeldPolicyRejected("reviewed public local pins have changed")
    return value


def classify(observed_license: str, *, proposed_release_license: str | None = None) -> dict:
    """Classify evidence, never return an ALLOW result even for an allowlisted version."""
    if observed_license not in LICENSES:
        return {"decision": "HELD_UNRECOGNIZED_LICENSE", "allowlisted": False, "public_release_eligible": False}
    if proposed_release_license is not None and proposed_release_license != observed_license:
        raise HeldPolicyRejected("license version relabel/upgrade prohibited")
    legal_code, version, sharealike, allowlisted = LICENSES[observed_license]
    return {
        "observed_license": observed_license,
        "legal_code": legal_code,
        "version": version,
        "sharealike_for_adaptations": sharealike,
        "allowlisted": allowlisted,
        "decision": ("HELD_FILE_LEVEL_RIGHTS_UNVERIFIED" if allowlisted
                     else "HELD_VERSION_CLASS_NOT_ACCEPTED"),
        "public_release_eligible": False,
    }


def validate(packet: dict, *, root: Path = ROOT) -> None:
    if not isinstance(packet, dict):
        raise HeldPolicyRejected("policy decision must be a JSON object")
    bases = _release_bases(root)
    fixed = {
        "packet_id": "librarian-cc-license-version-held-policy-20261104",
        "accepted_github_main": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "decision_type": "ADVISORY_HELD_LICENSE_VERSION_TRIAGE_NOT_PUBLIC_RELEASE_POLICY",
        "license_version_relabeling_or_upgrading_permitted": False,
        "source_license_must_remain_preserved_with_explicit_grant_route": True,
        "license_metadata_not_equivalent_to_personality_trademark_or_endorsement_clearance": True,
        "public_release_eligible": False,
        "public_artwork_release_effect": "NONE",
        "source_work_admission_effect": "NONE",
        "coverage_effect": "NONE",
    }
    if set(packet) != set(fixed) | {"accepted_release_gate", "version_policy", "accepted_source_examples", "alternatives_for_legacy_2_0"}:
        raise HeldPolicyRejected("unexpected policy/effect field")
    for key, value in fixed.items():
        _match(packet.get(key), value, key)
    accepted = packet.get("accepted_release_gate")
    if not isinstance(accepted, dict):
        raise HeldPolicyRejected("release policy receipt absent")
    _match(accepted, {
        "path": RELEASE_GATE, "sha256": RELEASE_GATE_SHA, "license_bases": sorted(bases),
        "reviewed_local_artwork_pin_count": 0, "release_gate_modified": False,
    }, "accepted_release_gate")
    policy = packet.get("version_policy")
    if not isinstance(policy, dict) or set(policy) != set(LICENSES):
        raise HeldPolicyRejected("CC license version policy missing or expanded")
    for identifier, (url, version, sa, supported) in LICENSES.items():
        _match(policy.get(identifier), {
            "legal_code": url, "source_version": version, "requires_sharealike_if_adapted": sa,
            "release_gate_allowlisted": supported,
            "decision": classify(identifier)["decision"], "default_future_route": "PRESERVE_HELD",
        }, f"version_policy.{identifier}")
        _match(identifier in bases, supported, f"allowlist.{identifier}")
    cases = packet.get("accepted_source_examples")
    if not isinstance(cases, list) or len(cases) != len(SOURCE_EXAMPLES):
        raise HeldPolicyRejected("source case inventory changed")
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or case.get("case_id") not in SOURCE_EXAMPLES:
            raise HeldPolicyRejected("unexpected source case")
        key = case["case_id"]
        if key in ids:
            raise HeldPolicyRejected("duplicate source case")
        ids.add(key)
        path, sha, label, raw_label, kind, decision, nested_id, expected_rights_field = SOURCE_EXAMPLES[key]
        source_path = root / path
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != sha:
            raise HeldPolicyRejected(f"accepted source SHA drift: {key}")
        original = _json(source_path)
        if nested_id is not None:
            originals = original.get("commons_alternative_candidates")
            original = next((item for item in originals if item.get("candidate_id") == nested_id), None)
            if original is None:
                raise HeldPolicyRejected("nested 4.0 source candidate not found")
        rights_field = case.get("rights_limit_field")
        raw_url_field = case.get("raw_license_url_field")
        if rights_field != expected_rights_field or \
                raw_url_field != "license_url" or not original.get(rights_field):
            raise HeldPolicyRejected("third-party rights limitation missing")
        if original.get("license") != raw_label or original.get(raw_url_field) != \
                LICENSES[label][0].replace("legalcode", ""):
            raise HeldPolicyRejected("underlying source's exact reported license/version changed")
        kind_field = ("candidate_use" if nested_id is not None else
                      "image_kind" if key == "beyond-premiere-photo-cc-by-2" else "photo_kind")
        if original.get(kind_field) != kind:
            raise HeldPolicyRejected("source asset-kind evidence changed")
        expected = {
            "case_id": key, "source_path": path, "source_sha256": sha,
            "observed_source_license": label, "license_field": "license", "raw_license_value": raw_label,
            "raw_license_url_field": "license_url", "rights_limit_field": rights_field,
            "source_local_asset_kind": kind, "expected_decision": decision,
            "evidence_class": "ACCEPTED_SOURCE_METADATA_NOT_RELEASE_RIGHTS",
        }
        if nested_id is not None:
            expected["nested_candidate_id"] = nested_id
        _match(case, expected, f"case.{key}")
        _match(classify(label)["decision"], decision, f"classified case.{key}")
    routes = packet.get("alternatives_for_legacy_2_0")
    if not isinstance(routes, list) or len(routes) != len(EXPECTED_ROUTES):
        raise HeldPolicyRejected("legacy route inventory changed")
    found = set()
    for route in routes:
        if not isinstance(route, dict) or route.get("route") not in EXPECTED_ROUTES:
            raise HeldPolicyRejected("unexpected policy route")
        key = route["route"]
        if key in found:
            raise HeldPolicyRejected("duplicate policy route")
        found.add(key)
        status, required = EXPECTED_ROUTES[key]
        _match(route.get("current_status"), status, f"route.{key}")
        _match(route.get("automatically_approves_publication"), False, f"route.{key}.approval")
        if set(route) != {"route", "current_status", "preconditions_for_future_release", "automatically_approves_publication"}:
            raise HeldPolicyRejected("route prerequisites missing or unexpected release field")
        _match(route.get("preconditions_for_future_release"), required, f"route.{key}.prerequisites")


def main() -> int:
    try:
        check_packet_inventory()
        validate(_json(PACKET / "records.json"))
    except (HeldPolicyRejected, OSError, ValueError, SyntaxError) as exc:
        print(f"CC_VERSION_HELD_POLICY_INVALID: {exc}", file=sys.stderr)
        return 1
    print("CC_VERSION_HELD_POLICY_OK: 2 legacy CC2 cases + 1 CC4 case; all HELD; public gate unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
