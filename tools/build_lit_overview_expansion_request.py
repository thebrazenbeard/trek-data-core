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
OUTPUT = 'proposals/publication/lit-overview-expansion-20261103/editorial-request.json'
ROW_COMMON_FIELDS = frozenset({
    'candidate_id', 'title', 'creator', 'series', 'format', 'isbn13', 'imprint',
    'publisher_publication_date', 'publisher_extent', 'publisher_url', 'synopsis_status', 'synopsis',
})
ROW_COVER_FIELDS = frozenset({'cover_candidate_locator', 'cover_locator_source', 'cover_rights_status'})
ROW_LIBRARIAN_FIELDS = frozenset({'existing_librarian_candidate_id', 'observation_verdict'})
ROOT_COMMON_FIELDS = frozenset({
    'schema_version', 'proposal_only', 'verification_class', 'distinct_upstream_sources',
    'candidate_work_count', 'accepted_source_work_effect', 'accepted_coverage_effect',
    'accepted_evidence_effect', 'source_bound', 'full_text_available', 'structurally_indexed',
    'close_read', 'semantically_analyzed', 'artwork_display_rights_verified',
    'publisher_edition_family_complete', 'candidate_works',
})
SOURCE_CONTRACTS = {
    INPUTS[0]: (
        'trek-lit-six-era-sns-publisher-v1',
        ROOT_COMMON_FIELDS | {'observed_on_utc', 'reader', 'independence_group',
                              'verified_edition_page_count', 'source_labeled_synopsis_count',
                              'cover_image_bytes_retrieved'},
        ROW_COMMON_FIELDS | ROW_COVER_FIELDS,
    ),
    INPUTS[1]: (
        'trek-lit-six-sns-work-discovery-v1',
        ROOT_COMMON_FIELDS | {'observed_on_utc', 'reader_class', 'independence_group',
                              'edition_page_count', 'synopsis_count'},
        ROW_COMMON_FIELDS | ROW_LIBRARIAN_FIELDS,
    ),
    INPUTS[2]: (
        'trek-lit-six-series-sns-publisher-v1',
        ROOT_COMMON_FIELDS | {'observed_utc_date', 'role', 'publisher_lineage',
                              'verified_edition_page_count', 'source_labeled_synopsis_count',
                              'cover_url_locators_held_count', 'cover_image_bytes_retrieved'},
        ROW_COMMON_FIELDS | ROW_COVER_FIELDS,
    ),
}
SOURCE_VARIANT_FIELDS = {
    INPUTS[0]: {
        'verification_class': 'DIRECT_OFFICIAL_PUBLISHER_PAGE_EDITION_METADATA_AND_DESCRIPTION',
        'reader': 'RENDERED_WEB_READER_NO_RAW_PAGE_BYTE_CUSTODY',
        'verified_edition_page_count': 6,
        'source_labeled_synopsis_count': 6,
    },
    INPUTS[1]: {
        'verification_class': 'DIRECT_PUBLISHER_EDITION_METADATA_AND_PROMOTIONAL_DESCRIPTION',
        'reader_class': 'RENDERED_OFFICIAL_PUBLISHER_PAGE_NO_RAW_HTML_CUSTODY',
        'edition_page_count': 6,
        'synopsis_count': 6,
    },
    INPUTS[2]: {
        'verification_class': 'DIRECT_OFFICIAL_PUBLISHER_PAGE_EDITION_METADATA_AND_DESCRIPTION',
        'role': 'LIT',
        'verified_edition_page_count': 6,
        'source_labeled_synopsis_count': 6,
        'cover_url_locators_held_count': 6,
    },
}


class CandidateError(ValueError):
    pass


def _closed_fields(value: object, fields: frozenset[str], context: str) -> None:
    if type(value) is not dict or set(value) != fields:
        raise CandidateError(f'Unexpected or missing {context} fields')


def _distinct_json_fields(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError('Duplicate JSON field')
        result[key] = value
    return result


def _read(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(ROOT):
        raise CandidateError(f'Non-custodied local input: {path}')
    return target.read_bytes()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(path: str) -> dict:
    value = json.loads(_read(path), object_pairs_hook=_distinct_json_fields)
    if not isinstance(value, dict):
        raise CandidateError(f'Not a JSON object: {path}')
    return value


def _render(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def _official_url(url: str, isbn: str) -> None:
    if not isinstance(url, str) or not isinstance(isbn, str) or len(isbn) != 13 or not isbn.isascii() or not isbn.isdigit():
        raise CandidateError('Missing publisher URL or ISBN')
    if sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(isbn)) % 10:
        raise CandidateError('Publisher ISBN-13 checksum invalid')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc != 'www.simonandschuster.com' or
            parsed.query or parsed.fragment or parsed.path.rsplit('/', 1)[-1] != isbn or
            not parsed.path.startswith('/books/')):
        raise CandidateError(f'Publisher edition URL does not bind its ISBN: {url}')


def _contains_private_path(value: str) -> bool:
    return re.search(r'(?i)[a-z]:[\\/]|[\\/](?:users|home|mnt|private)[\\/]', value) is not None


def _candidate(raw: dict, source: str, digest: str) -> dict:
    contract = SOURCE_CONTRACTS.get(source)
    if contract is None:
        raise CandidateError('Unknown editorial source contract')
    _closed_fields(raw, contract[2], 'publisher candidate')
    for key in ('candidate_id', 'title', 'creator', 'series', 'isbn13', 'publisher_url', 'synopsis'):
        if not isinstance(raw.get(key), str) or not raw[key].strip() or raw[key] != raw[key].strip():
            raise CandidateError(f'Missing exact {key} in {source}')
    for key in ('title', 'creator', 'series', 'publisher_publication_date', 'publisher_extent'):
        if (type(raw[key]) is not str or not raw[key] or len(raw[key]) > 200 or
                any(ord(char) < 32 for char in raw[key]) or
                _contains_private_path(raw[key])):
            raise CandidateError(f'Unsafe publisher {key} metadata')
    if raw.get('imprint') not in ('Pocket Books/Star Trek', 'Simon Spotlight') or raw.get('format') not in ('TRADE_PAPERBACK', 'MASS_MARKET_PAPERBACK'):
        raise CandidateError('Unverified publisher edition format or imprint')
    if (re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw['publisher_publication_date']) is None or
            re.fullmatch(r'[1-9]\d{0,3} pages', raw['publisher_extent']) is None):
        raise CandidateError('Unverified publisher publication date or length')
    if raw.get('synopsis_status') != 'PUBLISHER_DESCRIPTION_PARAPHRASE':
        raise CandidateError('Publisher synopsis has unreviewed basis')
    if (not 40 <= len(raw['synopsis']) <= 700 or
            any(ord(c) < 32 or c in '<>' for c in raw['synopsis']) or
            _contains_private_path(raw['synopsis']) or
            any(marker in raw['synopsis'].casefold() for marker in
                ('private_host_path', 'full_book_text', 'rights_to_republish_cover', 'https://', 'http://'))):
        raise CandidateError('Unsuitable source-relative synopsis for independent review')
    _official_url(raw['publisher_url'], raw['isbn13'])
    cover = raw.get('cover_candidate_locator')
    if source == INPUTS[1]:
        if (raw['observation_verdict'] != 'DIRECT_PAGE_EDITION_FIELDS_VERIFIED' or
                raw['existing_librarian_candidate_id'] not in (None, raw['candidate_id'])):
            raise CandidateError('Unverified Librarian source-local crosswalk')
    else:
        if raw['cover_locator_source'] != 'PUBLISHER_HIGH_RES_IMAGE_LINK' or not isinstance(cover, str):
            raise CandidateError('Missing rights-held publisher cover locator')
        parsed = urlsplit(cover)
        if (parsed.scheme != 'https' or parsed.netloc != 'd28hgpri8am2if.cloudfront.net' or
                parsed.query or parsed.fragment or raw.get('cover_rights_status') != 'RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY' or
                f'/cvr{raw["isbn13"]}/' not in parsed.path or not parsed.path.endswith(f'-{raw["isbn13"]}_hr.jpg')):
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
        expected_schema, expected_fields, _ = SOURCE_CONTRACTS[source]
        _closed_fields(data, expected_fields, 'publisher source packet')
        if data['schema_version'] != expected_schema:
            raise CandidateError('Unknown publisher source packet schema')
        for key, expected in SOURCE_VARIANT_FIELDS[source].items():
            if type(data[key]) is not type(expected) or data[key] != expected:
                raise CandidateError('Unverified publisher source reader or evidence tier')
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
                data.get('structurally_indexed') is not False or data.get('semantically_analyzed') is not False or
                data.get('publisher_edition_family_complete') is not False or
                data.get('distinct_upstream_sources') != 1 or
                (('cover_image_bytes_retrieved' in data) and data['cover_image_bytes_retrieved'] is not False) or
                data.get('candidate_work_count') != 6 or type(data.get('candidate_works')) is not list or len(data['candidate_works']) != 6):
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
    return {
        'schema_version': '1.0.0',
        'request_state': 'PROPOSAL_FOR_DIRECTORY_AND_SEPARATE_EDITORIAL_REVIEW',
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
