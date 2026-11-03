"""Fail-closed validation of a *metadata-only* SFA artwork locator proposal.

The upstream publisher HTML is not republished here. The earlier source-local
proposal, which is itself not accepted source binding, is the only input.
Passing this validator never establishes image rights or episode contents.
"""

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
UPSTREAM_PATH = REPO_ROOT / "proposals/research/sfa-publisher-refresh-20261103/records.json"
EXPECTED_UPSTREAM_SHA256 = "e6965602a534a5976a371501b457eb91aa5e9375302fdc62c99a42fd9a4136d3"
EXPECTED_PUBLISHER_SHA256 = "c5753b461be1739321643286a5d9c69666d2b67b94e0fa8ab549bed2db67f332"
PUBLISHER_SOURCE = "sfa-cbs-studios-show-20261103"
UPSTREAM_EVIDENCE = "sfa-cbs-photo-filename-evidence"
LINE_LOCATOR = "HTML lines 1056-1150 in exact private CBS Studios response"
HOLD = "Filename and caption metadata do not verify visual appearance, fictional character, episode, plot, or permitted use."
FORBIDDEN_KEYS = {
    "image_url", "image_path", "asset_url", "thumbnail_url", "image_sha256",
    "image_binary", "image_bytes", "canonical_work_id", "canonical_episode_id",
    "source_binding_id", "scene", "transcript", "asserted_character_id",
}
PHOTO_LABEL = re.compile(r"SFA_200_[A-Z0-9_]+\.(?:jpg|JPG)\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def forbid_promotion(obj):
    if isinstance(obj, dict):
        require(not (FORBIDDEN_KEYS & obj.keys()), "forbidden image/Work promotion key")
        for value in obj.values():
            forbid_promotion(value)
    elif isinstance(obj, list):
        for value in obj:
            forbid_promotion(value)


def validate(data, upstream, upstream_bytes):
    require(isinstance(data, dict) and isinstance(upstream, dict), "expected JSON objects")
    require(set(data) == {
        "schema_version", "batch_id", "role", "status", "accepted_source_binding_effect",
        "accepted_work_effect", "coverage_effect", "denominator_effect",
        "public_artwork_release_effect", "image_bytes_retrieved",
        "image_bytes_committed", "photo_contents_inspected", "rights_cleared",
        "external_rights_request_sent", "budget_committed_usd", "upstream_proposal",
        "rights_review", "candidate_photo_locators", "unresolved",
    }, "unexpected proposal field")
    require(hashlib.sha256(upstream_bytes).hexdigest() == EXPECTED_UPSTREAM_SHA256, "upstream publisher proposal changed")
    require(upstream.get("batch_id") == "SFA-PRESS-REFRESH-20261103-001" and upstream.get("status") == "PROPOSAL_ONLY_PUBLISHER_METADATA", "wrong upstream status")
    require(upstream.get("coverage_effect") == "NONE" and upstream.get("accepted_source_binding_effect") == "NONE", "upstream is no longer proposal-only")
    require(data.get("schema_version") == "1.0.0" and data.get("batch_id") == "SFA-ARTWORK-METADATA-20261103-001", "wrong candidate batch")
    require(data.get("role") == "SFA" and data.get("status") == "PROPOSAL_ONLY_SOURCE_RELATIVE_ARTWORK_METADATA", "wrong worker boundary")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "public_artwork_release_effect"):
        require(data.get(key) == "NONE", f"forbidden promotion: {key}")
    for key in ("image_bytes_retrieved", "image_bytes_committed", "photo_contents_inspected", "rights_cleared", "external_rights_request_sent"):
        require(data.get(key) is False, f"unverified action: {key}")
    require(type(data.get("budget_committed_usd")) is int and data["budget_committed_usd"] == 0, "fee commitment is unauthorized")
    forbid_promotion(data)

    source = next((s for s in upstream["source_snapshots"] if s["source_id"] == PUBLISHER_SOURCE), None)
    require(source is not None and source.get("independence_group") == "publisher:paramount", "lost publisher lineage")
    require(source.get("raw_response_sha256") == EXPECTED_PUBLISHER_SHA256, "changed publisher response receipt")
    require(source.get("snapshot_bytes_public") is False, "publisher HTML is not approved for public release")
    evidence = next((e for e in upstream["evidence"] if e["id"] == UPSTREAM_EVIDENCE), None)
    require(evidence is not None and evidence.get("source_id") == PUBLISHER_SOURCE, "wrong photo evidence source")
    require(evidence.get("kind") == "PUBLISHER_PHOTO_FILENAME_AND_CAPTION_LISTING", "wrong evidence class")
    require(evidence.get("locator") == LINE_LOCATOR, "source locator changed")
    upstream_photos = upstream["photo_metadata_observations"]
    require(len(upstream_photos) == 3 and evidence.get("photo_metadata_ids") == [p["id"] for p in upstream_photos], "photo evidence mismatch")

    lineage = data.get("upstream_proposal", {})
    require(set(lineage) == {
        "path", "sha256", "status", "publisher_source_id", "publisher_source_url",
        "publisher_independence_group", "publisher_raw_response_sha256",
        "publisher_observed_after_retrieval_utc", "source_relative_evidence_id",
        "source_relative_evidence_locator", "private_source_snapshot_available_in_this_batch",
    }, "unexpected lineage field")
    require(lineage.get("path") == "proposals/research/sfa-publisher-refresh-20261103/records.json", "wrong upstream path")
    require(lineage.get("sha256") == EXPECTED_UPSTREAM_SHA256, "wrong upstream digest in records")
    require(lineage.get("status") == upstream["status"], "derivative misrepresents upstream class")
    require(lineage.get("publisher_source_id") == PUBLISHER_SOURCE, "wrong publisher source identity")
    require(lineage.get("publisher_source_url") == source["url"], "wrong publisher source URL")
    require(lineage.get("publisher_independence_group") == source["independence_group"], "invented independent publisher")
    require(lineage.get("publisher_raw_response_sha256") == source["raw_response_sha256"], "wrong publisher response digest")
    require(lineage.get("publisher_observed_after_retrieval_utc") == source["observed_after_retrieval_utc"], "wrong source observation timestamp")
    require(lineage.get("source_relative_evidence_id") == evidence["id"], "wrong source evidence ID")
    require(lineage.get("source_relative_evidence_locator") == evidence["locator"], "wrong photo HTML locator")
    require(lineage.get("private_source_snapshot_available_in_this_batch") is False, "source snapshot not independently retrieved")

    rights = data.get("rights_review", {})
    require(set(rights) == {
        "status", "license_receipt_sha256", "publisher_press_terms_url",
        "cbs_still_licensing_faq_url", "cbs_licensing_request_url", "note",
    }, "unexpected rights field")
    require(rights.get("status") == "NOT_ESTABLISHED" and rights.get("license_receipt_sha256") is None, "unverified image rights")
    require(rights.get("publisher_press_terms_url") == "https://www.paramount.com/paramount-press-express-terms-of-use", "wrong press terms")
    require(rights.get("cbs_still_licensing_faq_url") == "https://www.cbsfootagelicensing.com/faq", "wrong official licensing FAQ")
    require(rights.get("cbs_licensing_request_url") == "https://www.cbsfootagelicensing.com/request", "wrong licensing request route")
    require(isinstance(rights.get("note"), str) and "No authorization" in rights["note"], "missing rights hold")

    candidates = data.get("candidate_photo_locators")
    require(isinstance(candidates, list) and len(candidates) == 3, "expected exactly three source photo locators")
    require(len({c.get("candidate_id") for c in candidates}) == 3, "duplicate candidate ID")
    for i, (candidate, parent) in enumerate(zip(candidates, upstream_photos), start=1):
        require(set(candidate) == {
            "candidate_id", "upstream_photo_metadata_id", "publisher_source_id",
            "source_relative_html_line", "file_label",
            "caption_subjects_as_publisher_metadata", "candidate_kind", "rights_status",
            "image_bytes_retrieved", "public_display_effect", "interpretation_hold",
        }, "unexpected candidate field")
        require(candidate.get("candidate_id") == f"sfa-artwork-20261103-photo-200-{i:02d}", "wrong source-local candidate ID")
        require(candidate.get("upstream_photo_metadata_id") == parent["id"], "photo ID relinked")
        require(candidate.get("publisher_source_id") == source["source_id"], "photo source relinked")
        require(candidate.get("source_relative_html_line") == parent["raw_html_line"], "photo line locator altered")
        require(candidate.get("file_label") == parent["file_label"] and PHOTO_LABEL.fullmatch(candidate["file_label"]), "publisher filename altered")
        require(candidate.get("caption_subjects_as_publisher_metadata") == parent["caption_subjects"], "publisher caption altered")
        require(candidate.get("candidate_kind") == "PUBLISHER_PHOTO_FILENAME_CAPTION_REFERENCE", "unsupported art evidence")
        require(candidate.get("rights_status") == "NOT_ESTABLISHED", "unreviewed thumbnail permission")
        require(candidate.get("image_bytes_retrieved") is False, "unobserved image bytes")
        require(candidate.get("public_display_effect") == "NONE", "public sidecar effect prohibited")
        require(candidate.get("interpretation_hold") == HOLD, "photo content/episode misinterpretation")
    unresolved = data.get("unresolved")
    require(isinstance(unresolved, list) and len(unresolved) == 4, "missing uncertainty ledger")
    require(all(isinstance(v, str) and v for v in unresolved), "invalid uncertainty")
    return len(candidates)


def main():
    upstream_bytes = UPSTREAM_PATH.read_bytes()
    upstream = json.loads(upstream_bytes)
    data = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    count = validate(data, upstream, upstream_bytes)
    print(f"SFA_ARTWORK_LOCATORS_PASS: {count} publisher caption/filename locators; 0 image bytes; 0 display licenses; 0 accepted Works")


if __name__ == "__main__":
    main()
