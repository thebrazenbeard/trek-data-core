"""Fail-closed static checks for this candidate-only artwork source tranche."""

import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "artwork-source-candidates-20261103" / "records.json"
ALLOWED_HOSTS = {
    "commons.wikimedia.org",
    "developer.themoviedb.org",
    "openlibrary.org",
    "creativecommons.org",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def validate():
    proposal = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    for flag in ("proposal_only",):
        check(proposal.get(flag) is True, f"expected candidate-only flag: {flag}")
    for effect in (
        "accepted_source_binding_effect",
        "accepted_work_effect",
        "coverage_effect",
        "public_artwork_release_effect",
    ):
        check(proposal.get(effect) == "NONE", f"unexpected promotion: {effect}")
    check(proposal.get("image_bytes_committed") is False, "image release is prohibited")

    assets = proposal.get("asset_candidates")
    providers = proposal.get("provider_routes")
    check(isinstance(assets, list) and assets, "missing asset candidates")
    check(isinstance(providers, list) and providers, "missing provider routes")
    existing_ids = {item["candidate_id"] for item in previous["candidates"]}
    current_ids = set()
    for asset in assets:
        ident = asset.get("candidate_id")
        check(isinstance(ident, str) and ident not in existing_ids and ident not in current_ids,
              "duplicate or invalid candidate id")
        current_ids.add(ident)
        check(asset.get("target_scope") == "REPOSITORY_BRANDING_CANDIDATE",
              "logo/insignia must not be an episode or film Work")
        check(asset.get("display_status", "").startswith("BLOCK_PENDING_"),
              "brand artwork cannot bypass rights review")
        check(asset.get("release_asset_path") is None, "unreviewed artwork path present")
        check(asset.get("source_sha1_independently_recomputed") is False,
              "source hash cannot be promoted from a file-page claim")
        check(asset.get("source_page_url", "").startswith("https://commons.wikimedia.org/wiki/File:"),
              "asset lacks a Commons file-description identity")
        check("oldid=" in asset.get("source_revision_url", ""), "unversioned Commons observation")
        for key in ("source_page_url", "source_revision_url", "source_license_url"):
            value = asset.get(key)
            if value is not None:
                parsed = urlsplit(value)
                check(parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS and not parsed.username,
                      f"unexpected URL origin: {key}")

    seen_provider_ids = set()
    for provider in providers:
        ident = provider.get("provider_id")
        check(isinstance(ident, str) and ident not in seen_provider_ids, "duplicate provider id")
        seen_provider_ids.add(ident)
        check(provider.get("display_status") != "PUBLIC_DISPLAY_PERMISSION_VERIFIED",
              "policy docs cannot grant rights to specific images")
        check("image_path" not in provider and "image_url" not in provider,
              "provider route must not become an image release")
        check(provider.get("required_conditions"), "missing provider approval gates")
        for key, value in provider.items():
            if key.endswith("_url") and value is not None:
                parsed = urlsplit(value)
                check(parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS and not parsed.username,
                      f"unexpected provider URL origin: {key}")
    print(f"PASS: {len(assets)} blocked identity asset candidates; "
          f"{len(providers)} gated provider routes; no public artwork release")


if __name__ == "__main__":
    validate()
