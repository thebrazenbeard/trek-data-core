#!/usr/bin/env python3
"""Append-only literary modal corrections over the strict accepted v1 compiler.

The original publisher observations and editorial request remain untouched.
This creates a proposed *new* review request; it does not publish copy.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys

from build_lit_overview_expansion_request import (
    CandidateError, OUTPUT as LEGACY_OUTPUT, ROOT, _contains_private_path,
    _json, _read, _render, _sha, build as build_legacy,
)

CORRECTIONS = 'proposals/research/lit-overview-supersession-v2-20261103/records.json'
OUTPUT = 'proposals/publication/lit-overview-expansion-20261103/editorial-request-v2.json'
ORIGINAL_SOURCE = 'proposals/research/lit-six-next-publisher-works-20261103/observations.json'
TARGETS = {
    'lit-source-local-sns-discovery-somewhere-to-belong-20261103': (
        '9781668002292', 'UNSUPPORTED_ASSERTED_OUTCOME_RESTORED_TO_PUBLISHER_MODALITY',
        'may lead to a new crisis', 'draws them into new danger',
    ),
    'lit-source-local-sns-picard-firewall-20261103': (
        '9781668046364', 'PUBLISHER_ASSERTED_EVENT_UNDERSTATED_AS_CONSIDERATION',
        'finds a new home with the Fenris Rangers', 'considers joining',
    ),
}
ROOT_KEYS = {
    'schema_version', 'proposal_only', 'observed_on_utc', 'supersedes_source_path',
    'supersedes_source_sha256', 'prior_editorial_request_path',
    'prior_editorial_request_sha256', 'source_class', 'source_group',
    'independent_source_count', 'correction_count', 'accepted_source_work_effect',
    'accepted_coverage_effect', 'accepted_evidence_effect', 'public_release_effect',
    'original_source_packet_mutated', 'corrections',
}
CORRECTION_KEYS = {
    'candidate_work_id', 'publisher_edition_isbn13', 'publisher_edition_url',
    'prior_paraphrase_sha256', 'correction_kind', 'reason',
    'replacement_paraphrase', 'editorial_status',
}


def _valid_text(value: object, limit: int = 700) -> bool:
    return (type(value) is str and 40 <= len(value) <= limit and
            not any(ord(ch) < 32 or ch in '<>\u202e' for ch in value) and
            not _contains_private_path(value) and
            'http://' not in value.casefold() and 'https://' not in value.casefold())


def build() -> dict:
    legacy = build_legacy()  # Strict schema, duplicate-key, edition/URL/ISBN checks.
    original_bytes = _read(LEGACY_OUTPUT)
    if original_bytes != _render(legacy):
        raise CandidateError('Accepted v1 publisher request has drifted')
    corrections = _json(CORRECTIONS)
    if (set(corrections) != ROOT_KEYS or
            corrections['schema_version'] != 'trek-lit-overview-source-local-supersession-v2' or
            corrections['proposal_only'] is not True or
            corrections['observed_on_utc'] != '2026-11-03' or
            corrections['supersedes_source_path'] != ORIGINAL_SOURCE or
            corrections['supersedes_source_sha256'] != _sha(_read(ORIGINAL_SOURCE)) or
            corrections['prior_editorial_request_path'] != LEGACY_OUTPUT or
            corrections['prior_editorial_request_sha256'] != _sha(original_bytes) or
            corrections['source_class'] != 'DIRECT_RENDERED_OFFICIAL_PUBLISHER_ABOUT_THE_BOOK_NO_RAW_PAGE_CUSTODY' or
            corrections['source_group'] != 'publisher:simonandschuster.com' or
            type(corrections['independent_source_count']) is not int or
            corrections['independent_source_count'] != 1 or
            type(corrections['correction_count']) is not int or
            corrections['correction_count'] != 2 or
            corrections['original_source_packet_mutated'] is not False or
            any(corrections[key] != 'NONE' for key in (
                'accepted_source_work_effect', 'accepted_coverage_effect',
                'accepted_evidence_effect', 'public_release_effect')) or
            type(corrections['corrections']) is not list or
            len(corrections['corrections']) != 2):
        raise CandidateError('Correction provenance/version contract violated')

    result = copy.deepcopy(legacy)
    by_id = {row['candidate_work_id']: row for row in result['candidates']}
    seen = set()
    for correction in corrections['corrections']:
        if type(correction) is not dict or set(correction) != CORRECTION_KEYS:
            raise CandidateError('Unknown correction fields')
        ident = correction['candidate_work_id']
        if type(ident) is not str or ident not in TARGETS or ident in seen:
            raise CandidateError('Missing, unknown or duplicate modal correction target')
        seen.add(ident)
        isbn, kind, required, forbidden = TARGETS[ident]
        prior = by_id[ident]
        new_text = correction['replacement_paraphrase']
        reason = correction['reason']
        if (correction['publisher_edition_isbn13'] != isbn or
                correction['publisher_edition_isbn13'] != prior['publisher_edition_isbn13'] or
                correction['publisher_edition_url'] != prior['publisher_edition_url'] or
                prior['observation_path'] != ORIGINAL_SOURCE or
                correction['prior_paraphrase_sha256'] != prior['original_paraphrase_sha256'] or
                correction['correction_kind'] != kind or
                correction['editorial_status'] != 'INDEPENDENT_RECHECK_REQUIRED' or
                not _valid_text(new_text) or not isinstance(reason, str) or
                not reason.strip() or _contains_private_path(reason) or
                required not in new_text or forbidden in new_text):
            raise CandidateError('Modal correction source, text or edition mismatch')
        prior['original_paraphrase'] = new_text
        prior['original_paraphrase_sha256'] = _sha(new_text.encode('utf-8'))
        prior['display_supersession_source'] = CORRECTIONS
    if seen != set(TARGETS):
        raise CandidateError('Both mandatory modal corrections are required')
    for row in result['candidates']:
        row.setdefault('display_supersession_source', None)
    prefix = {
        'schema_version': result['schema_version'],
        'request_state': 'V2_SUPERSEDING_PROPOSAL_FOR_SEPARATE_EDITORIAL_REVIEW',
        'supersedes_review_request_path': LEGACY_OUTPUT,
        'supersedes_review_request_sha256': _sha(original_bytes),
        'source_local_correction_path': CORRECTIONS,
        'source_local_correction_sha256': _sha(_read(CORRECTIONS)),
        'corrected_paraphrase_count': 2,
    }
    # Keep the existing publisher-request projection's field order and identity
    # intact. The superseding manifest/header is visibly additive.
    return {**prefix, **{k: v for k, v in result.items()
                       if k not in {'schema_version', 'request_state'}}}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    try:
        data = _render(build())
        if args.check:
            if _read(OUTPUT) != data:
                raise CandidateError('V2 review request is not reproducible')
            print('LIT_MODAL_CORRECTIONS_V2_OK: 18 source-local candidates; two corrections, no release')
        else:
            (ROOT / OUTPUT).write_bytes(data)
            print('LIT_MODAL_CORRECTIONS_V2_WRITTEN: review request only')
    except (OSError, CandidateError, ValueError) as exc:
        print(f'LIT_MODAL_CORRECTIONS_HELD: {exc}', file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
