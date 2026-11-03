#!/usr/bin/env python3
"""Review-gated optional literary candidate synopsis sidecar; no directory mutation.

This compiler does not judge synopses or reconcile global Work identity. It
merely enforces a separately authored exact-text editorial decision before
turning accepted source-relative research into a display-only sidecar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from build_lit_overview_expansion_request import CandidateError, ROOT, _read, _render
from build_lit_modal_corrected_request import OUTPUT as REQUEST_PATH, build

REVIEW_PATH = 'proposals/reviews/model-editorial-lit-overviews-18-20261103/receipt.json'
PUBLIC_PATH = 'explorer/literary-candidate-overviews.json'
# No review is approved at this checkpoint. A separate authorized, reviewed
# change must pin the exact accepted receipt bytes before any release attempt.
# A self-authored JSON claim of independent review is not authentication.
APPROVED_RECEIPT_SHA256: str | None = None


class ReleaseError(ValueError):
    pass


def _sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _load(path: str) -> dict:
    data = json.loads(_read(path))
    if not isinstance(data, dict):
        raise ReleaseError('Review evidence must be a JSON object')
    return data


def _expected_source_tuples(request: dict) -> list[tuple[str, str, str]]:
    return sorted((c['candidate_work_id'], c['publisher_edition_url'], c['original_paraphrase_sha256'])
                  for c in request['candidates'])


def verify_receipt(request: dict, receipt: dict) -> str:
    receipt_sha = _sha(_read(REVIEW_PATH))
    if APPROVED_RECEIPT_SHA256 is None or receipt_sha != APPROVED_RECEIPT_SHA256:
        raise ReleaseError('Editorial receipt lacks a separately approved immutable hash pin')
    exact_keys = {
        'schema_version', 'review_kind', 'review_result', 'reviewer_agent', 'provider', 'runtime',
        'review_independence', 'review_request_sha256', 'reviewed_on_utc', 'reviewed_source_tuples',
        'reviewed_paraphrase_count', 'passed_paraphrase_count', 'failed_paraphrase_count',
        'review_method', 'limitations', 'coverage_effect', 'source_work_admission_effect',
        'artwork_release_effect',
    }
    if (set(receipt) != exact_keys or receipt.get('schema_version') != '1.0.0' or
            receipt.get('review_kind') != 'MODEL_EDITORIAL_REVIEW' or
            receipt.get('review_result') != 'PASS_18_OFFICIAL_PUBLISHER_PARAPHRASES_FOR_DISPLAY_ONLY' or
            receipt.get('reviewer_agent') != '/root/repo_workflow_merger_audit' or
            receipt.get('provider') != 'OpenAI' or
            receipt.get('runtime') != 'ChatGPT native subagent (model identity not externally attested)' or
            receipt.get('review_independence') != 'SEPARATE_MODEL_AGENT_FROM_CANDIDATE_AND_RELEASE_AUTHORS' or
            receipt.get('review_request_sha256') != _sha(_render(request)) or
            receipt.get('reviewed_on_utc') != '2026-11-03' or
            receipt.get('reviewed_paraphrase_count') != 18 or
            receipt.get('passed_paraphrase_count') != 18 or receipt.get('failed_paraphrase_count') != 0 or
            any(receipt.get(key) != 'NONE' for key in ('coverage_effect', 'source_work_admission_effect',
                                                      'artwork_release_effect')) or
            not isinstance(receipt.get('review_method'), str) or not receipt['review_method'].strip() or
            not isinstance(receipt.get('limitations'), list) or not receipt['limitations']):
        raise ReleaseError('A separate, exact model-editorial approval is required')
    tuples = receipt.get('reviewed_source_tuples')
    if not isinstance(tuples, list) or len(tuples) != 18 or any(
            not isinstance(row, list) or len(row) != 3 or any(not isinstance(x, str) for x in row)
            for row in tuples):
        raise ReleaseError('Review lacked exact candidate/source/text tuples')
    if sorted(map(tuple, tuples)) != _expected_source_tuples(request):
        raise ReleaseError('Publisher edition or synopsis changed after independent review')
    return receipt_sha


def release(request: dict, receipt: dict) -> dict:
    reviewer_sha = verify_receipt(request, receipt)
    rows = []
    for candidate in request['candidates']:
        rows.append({
            'row_id': 'candidate:' + candidate['proposed_directory_row_id'],
            'source_local_candidate_id': candidate['candidate_work_id'],
            'title': candidate['title'],
            'creator': candidate['creator'],
            'series': candidate['series'],
            'medium': 'LITERATURE',
            'publisher_edition_isbn13': candidate['publisher_edition_isbn13'],
            'source_locator': candidate['publisher_edition_url'],
            'overview_evidence_locator': candidate['overview_evidence_url'],
            'overview_text': candidate['original_paraphrase'],
            'overview_basis': 'PUBLISHER_DESCRIPTION_PARAPHRASE',
            'observation_path': candidate['observation_path'],
            'observation_sha256': candidate['observation_sha256'],
            'original_paraphrase_sha256': candidate['original_paraphrase_sha256'],
            'source_correction_path': candidate['display_supersession_source'],
            'editorial_receipt_sha256': reviewer_sha,
            'raw_webpage_sha256': None,
            'identity_status': 'SOURCE_LOCAL_UNRECONCILED',
            'accepted_directory_row_id': None,
            'artwork_release_effect': 'NONE',
            'coverage_effect': 'NONE',
            'admission_effect': 'NONE',
        })
    return {
        'schema_version': '1.0.0',
        'data_status': 'SOURCE_LOCAL_PUBLISHER_CANDIDATES_EDITORIALLY_REVIEWED_DISPLAY_ONLY',
        'source_group': 'publisher:simonandschuster.com',
        'independence_group_count': 1,
        'separate_from_directory': True,
        'directory_snapshot_rows_unchanged': request['accepted_directory_snapshot_row_count'],
        'candidate_count': len(rows),
        'review_request_sha256': _sha(_render(request)),
        'source_local_correction_sha256': request['source_local_correction_sha256'],
        'editorial_receipt_sha256': reviewer_sha,
        'admission_effect': 'NONE',
        'coverage_effect': 'NONE',
        'artwork_release_effect': 'NONE',
        'candidates': rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        request = build()
        if _read(REQUEST_PATH) != _render(request):
            raise ReleaseError('Source-proposal review request is stale')
        result = _render(release(request, _load(REVIEW_PATH)))
        if args.check:
            if _read(PUBLIC_PATH) != result:
                raise ReleaseError('Public literary candidate sidecar is stale')
            print('LITERARY_CANDIDATE_RELEASE_OK: 18 publisher-description overviews; no admitted Works')
        else:
            target = ROOT / PUBLIC_PATH
            target.write_bytes(result)
            print('LITERARY_CANDIDATE_RELEASE_WRITTEN: review-gated, no directory mutation')
    except (CandidateError, ReleaseError, OSError, ValueError) as exc:
        print(f'LITERARY_CANDIDATE_RELEASE_HELD: {exc}', file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
