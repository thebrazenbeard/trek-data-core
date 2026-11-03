#!/usr/bin/env python3
"""Compile an editorial *request*, not a published literary synopsis catalog.

Accepted publisher research remains source-local discovery. A proposed directory
row is deliberately not an accepted Work, accepted identity reconciliation, or
permission to display a cover or description on the public Explorer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    'proposals/research/lit-six-era-publisher-20261103/observations.json',
    'proposals/research/lit-six-next-publisher-works-20261103/observations.json',
    'proposals/research/lit-six-series-expansion-20261103/observations.json',
)
LEGACY_OUTPUT = 'proposals/publication/lit-overview-expansion-20261103/editorial-request.json'
CORRECTIONS = 'proposals/research/lit-overview-supersession-v2-20261103/records.json'
OUTPUT = 'proposals/publication/lit-overview-expansion-20261103/editorial-request-v2.json'


class CandidateError(ValueError):
    pass


def _read(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(ROOT):
        raise CandidateError(f'Non-custodied local input: {path}')
    return target.read_bytes()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(path: str) -> dict:
    value = json.loads(_read(path))
    if not isinstance(value, dict):
        raise CandidateError(f'Not a JSON object: {path}')
    return value


def _render(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def _official_url(url: str, isbn: str) -> None:
    if not isinstance(url, str) or not isinstance(isbn, str) or len(isbn) != 13 or not isbn.isascii() or not isbn.isdigit():
        raise CandidateError('Missing publisher URL or ISBN')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc != 'www.simonandschuster.com' or
            parsed.query or parsed.fragment or parsed.path.rsplit('/', 1)[-1] != isbn or
            not parsed.path.startswith('/books/')):
        raise CandidateError(f'Publisher edition URL does not bind its ISBN: {url}')


def _candidate(raw: dict, source: str, digest: str) -> dict:
    for key in ('candidate_id', 'title', 'creator', 'series', 'isbn13', 'publisher_url', 'synopsis'):
        if not isinstance(raw.get(key), str) or not raw[key].strip() or raw[key] != raw[key].strip():
            raise CandidateError(f'Missing exact {key} in {source}')
    if raw.get('synopsis_status') != 'PUBLISHER_DESCRIPTION_PARAPHRASE':
        raise CandidateError('Publisher synopsis has unreviewed basis')
    if not 40 <= len(raw['synopsis']) <= 700 or any(ord(c) < 32 or c in '<>' for c in raw['synopsis']):
        raise CandidateError('Unsuitable source-relative synopsis for independent review')
    _official_url(raw['publisher_url'], raw['isbn13'])
    cover = raw.get('cover_candidate_locator')
    if cover is not None:
        parsed = urlsplit(cover)
        if (parsed.scheme != 'https' or parsed.netloc != 'd28hgpri8am2if.cloudfront.net' or
                parsed.query or parsed.fragment or raw.get('cover_rights_status') != 'RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY'):
            raise CandidateError('Cover candidate rights or source URL violated')
    if re.fullmatch(r'(?:proposed-lit-|lit-source-local-sns-)[a-z0-9-]+', raw['candidate_id']) is None:
        raise CandidateError('Unsafe source-local candidate key')
    return {
        'candidate_work_id': raw['candidate_id'],
        'proposed_directory_row_id': 'literature:' + raw['candidate_id'],
        'accepted_directory_row_id': None,
        'identity_status': 'SOURCE_LOCAL_UNRECONCILED',
        'title': raw['title'],
        'creator': raw['creator'],
        'series': raw['series'],
        'publisher_edition_isbn13': raw['isbn13'],
        'publisher_edition_url': raw['publisher_url'],
        'overview_evidence_url': raw['publisher_url'],
        'original_paraphrase': raw['synopsis'],
        'original_paraphrase_sha256': _sha(raw['synopsis'].encode('utf-8')),
        'overview_basis': 'PUBLISHER_DESCRIPTION_PARAPHRASE',
        'observation_path': source,
        'observation_sha256': digest,
        'raw_webpage_sha256': None,
        'artwork_candidate_locator': cover,
        'artwork_release_status': 'HELD_NO_PUBLIC_DISPLAY',
        'editorial_review_status': 'INDEPENDENT_REVIEW_REQUIRED',
        'public_release_status': 'NOT_RELEASED',
        'accepted_work_effect': 'NONE',
        'accepted_coverage_effect': 'NONE',
    }


def build() -> dict:
    directory = _json('explorer/discovery-catalog.json')
    accepted_rows = directory['rows']
    if len(accepted_rows) != directory['row_count'] or directory['data_status'] != 'DISCOVERY_ONLY':
        raise CandidateError('Accepted directory is inconsistent')
    used_row_ids = {row['row_id'] for row in accepted_rows}
    used_titles = {row['title'].casefold() for row in accepted_rows if row['medium'] == 'LITERATURE'}
    candidates = []
    source_artifacts = []
    for source in INPUTS:
        data = _json(source)
        series_packet = data.get('schema_version') == 'trek-lit-six-series-sns-publisher-v1'
        date_key = 'observed_utc_date' if series_packet else 'observed_on_utc'
        lineage_key = 'publisher_lineage' if series_packet else 'independence_group'
        for key in ('accepted_source_work_effect', 'accepted_coverage_effect', 'accepted_evidence_effect'):
            if data.get(key) != 'NONE':
                raise CandidateError(f'Unexpected accepted effect in source proposal: {source}')
        if (data.get('proposal_only') is not True or data.get(date_key) != '2026-11-03' or
                data.get(lineage_key) != 'publisher:simonandschuster.com' or
                data.get('source_bound') is not False or data.get('close_read') is not False or
                data.get('full_text_available') is not False or data.get('artwork_display_rights_verified') is not False or
                data.get('candidate_work_count') != 6 or len(data.get('candidate_works', [])) != 6):
            raise CandidateError(f'Not source-local six-title discovery: {source}')
        digest = _sha(_read(source))
        source_artifacts.append({'path': source, 'sha256': digest, 'candidate_count': 6})
        for raw in data['candidate_works']:
            entry = _candidate(raw, source, digest)
            if entry['proposed_directory_row_id'] in used_row_ids or entry['title'].casefold() in used_titles:
                raise CandidateError('Publisher candidate collides with existing directory observation')
            candidates.append(entry)
    ids = [entry['candidate_work_id'] for entry in candidates]
    titles = [entry['title'].casefold() for entry in candidates]
    isbns = [entry['publisher_edition_isbn13'] for entry in candidates]
    if len(ids) != 18 or any(len(set(values)) != 18 for values in (ids, titles, isbns)):
        raise CandidateError('Publisher candidate identity or edition duplicate')
    correction_data = _json(CORRECTIONS)
    prior_request_sha = _sha(_read(LEGACY_OUTPUT))
    superseded_source_path = 'proposals/research/lit-six-next-publisher-works-20261103/observations.json'
    if (correction_data.get('schema_version') != 'trek-lit-overview-source-local-supersession-v2' or
            correction_data.get('proposal_only') is not True or
            correction_data.get('observed_on_utc') != '2026-11-03' or
            correction_data.get('supersedes_source_path') != superseded_source_path or
            correction_data.get('supersedes_source_sha256') != _sha(_read(superseded_source_path)) or
            correction_data.get('prior_editorial_request_path') != LEGACY_OUTPUT or
            correction_data.get('prior_editorial_request_sha256') != prior_request_sha or
            correction_data.get('source_class') != 'DIRECT_RENDERED_OFFICIAL_PUBLISHER_ABOUT_THE_BOOK_NO_RAW_PAGE_CUSTODY' or
            correction_data.get('source_group') != 'publisher:simonandschuster.com' or
            correction_data.get('independent_source_count') != 1 or
            correction_data.get('correction_count') != 2 or
            len(correction_data.get('corrections', [])) != 2 or
            correction_data.get('original_source_packet_mutated') is not False or
            any(correction_data.get(k) != 'NONE' for k in ('accepted_source_work_effect',
                                                           'accepted_coverage_effect',
                                                           'accepted_evidence_effect',
                                                           'public_release_effect'))):
        raise CandidateError('Publisher correction provenance/version contract not satisfied')
    prior = _json(LEGACY_OUTPUT)
    prior_by_id = {row['candidate_work_id']: row for row in prior.get('candidates', [])}
    by_id = {row['candidate_work_id']: row for row in candidates}
    observed_corrections = set()
    for correction in correction_data['corrections']:
        ident = correction.get('candidate_work_id')
        if ident in observed_corrections or ident not in by_id or ident not in prior_by_id:
            raise CandidateError('Duplicate or absent candidate supersession target')
        original, old = by_id[ident], prior_by_id[ident]
        if (original['observation_path'] != superseded_source_path or
                correction.get('publisher_edition_isbn13') != original['publisher_edition_isbn13'] or
                correction.get('publisher_edition_url') != original['publisher_edition_url'] or
                correction.get('prior_paraphrase_sha256') != original['original_paraphrase_sha256'] or
                correction.get('prior_paraphrase_sha256') != old['original_paraphrase_sha256'] or
                correction.get('editorial_status') != 'INDEPENDENT_RECHECK_REQUIRED' or
                correction.get('correction_kind') not in (
                    'UNSUPPORTED_ASSERTED_OUTCOME_RESTORED_TO_PUBLISHER_MODALITY',
                    'PUBLISHER_ASSERTED_EVENT_UNDERSTATED_AS_CONSIDERATION') or
                not isinstance(correction.get('reason'), str) or not correction['reason'].strip()):
            raise CandidateError('Supersession does not bind the exact previous source/edition/text')
        new_text = correction.get('replacement_paraphrase')
        if not isinstance(new_text, str) or not 40 <= len(new_text) <= 700 or any(ord(c) < 32 or c in '<>' for c in new_text):
            raise CandidateError('Supersession text is not an original reviewable paraphrase')
        if (ident.endswith('somewhere-to-belong-20261103') and
                ('may lead to a new crisis' not in new_text or 'draws them into new danger' in new_text)) or (
                ident.endswith('picard-firewall-20261103') and
                ('finds a new home with the Fenris Rangers' not in new_text or 'considers joining' in new_text)):
            raise CandidateError('Known publisher modal regression reintroduced')
        original['original_paraphrase'] = new_text
        original['original_paraphrase_sha256'] = _sha(new_text.encode('utf-8'))
        original['display_supersession_source'] = CORRECTIONS
        observed_corrections.add(ident)
    if observed_corrections != {
        'lit-source-local-sns-discovery-somewhere-to-belong-20261103',
        'lit-source-local-sns-picard-firewall-20261103',
    }:
        raise CandidateError('Two material publisher modal corrections are mandatory')
    for entry in candidates:
        entry.setdefault('display_supersession_source', None)
    correction_digest = _sha(_read(CORRECTIONS))
    return {
        'schema_version': '1.0.0',
        'request_state': 'V2_SUPERSEDING_PROPOSAL_FOR_SEPARATE_EDITORIAL_REVIEW',
        'supersedes_review_request_path': LEGACY_OUTPUT,
        'supersedes_review_request_sha256': prior_request_sha,
        'source_local_correction_path': CORRECTIONS,
        'source_local_correction_sha256': correction_digest,
        'corrected_paraphrase_count': 2,
        'accepted_directory_snapshot_row_count': directory['row_count'],
        'accepted_directory_snapshot_sha256': _sha(_read('explorer/discovery-catalog.json')),
        'source_lineage_group': 'publisher:simonandschuster.com',
        'independent_source_count': 1,
        'candidate_count': len(candidates),
        'source_artifacts': source_artifacts,
        'coverage_effect': 'NONE',
        'source_work_evidence_admission_effect': 'NONE',
        'public_site_effect': 'NONE',
        'candidates': sorted(candidates, key=lambda row: row['proposed_directory_row_id']),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = _render(build())
    path = ROOT / OUTPUT
    if args.check:
        if _read(OUTPUT) != value:
            raise CandidateError('Editorial request is stale or manually modified')
        print('LITERARY_OVERVIEW_REQUEST_OK: 18 candidates, no public effect')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
        print('LITERARY_OVERVIEW_REQUEST_WRITTEN: 18 candidates, no public effect')


if __name__ == '__main__':
    main()
