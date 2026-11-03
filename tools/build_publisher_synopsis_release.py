#!/usr/bin/env python3
"""Deterministic, fail-closed publisher-description overview release builder.

Only accepted ORIGINAL source-proposal paraphrases are candidates. A separate
independent editorial receipt is required to turn a proposal into a public
display artifact; source pages were rendered, not byte-custodied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = (
    'proposals/research/lit-three-publisher-editions-20261103/observations.json',
    'proposals/research/lit-ring-memoir-publisher-20261103/observations.json',
    'proposals/research/films/publisher-synopses-20261103/observations.json',
)
REVIEW_PATH = 'proposals/reviews/model-editorial-publisher-overviews-20261103/receipt.json'
PUBLIC_PATH = 'explorer/synopsis-catalog.json'
REQUEST_PATH = 'proposals/publication/publisher-overviews-20261103/review-request.json'


class ReleaseError(ValueError):
    pass


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    """A last-key-wins parse cannot attest source or editorial effect fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError(f'Duplicate JSON key in publisher release input: {key!r}')
        result[key] = value
    return result


def _raw(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(ROOT):
        raise ReleaseError(f'Untrusted input path: {path}')
    return target.read_bytes()


def _load(path: str) -> dict:
    value = json.loads(_raw(path), object_pairs_hook=_unique_json_object)
    if not isinstance(value, dict):
        raise ReleaseError(f'Expected object: {path}')
    return value


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text_fingerprint(text: str) -> str:
    return _digest(text.encode('utf-8'))


def _canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def _pretty(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _url(value: str, hostname: str) -> str:
    if not isinstance(value, str):
        raise ReleaseError('Missing publisher locator')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or parsed.hostname != hostname or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
        raise ReleaseError(f'Publisher locator escaped exact host: {value}')
    return parsed.path


def _clean_synopsis(value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not (40 <= len(value) <= 700) or any(ord(ch) < 32 or ch in '<>' for ch in value):
        raise ReleaseError('Unreviewable publisher overview text')
    return value


def _source_artifact(path: str) -> tuple[dict, str]:
    value = _load(path)
    if value.get('proposal_only') is not True or value.get('observed_on_utc') != '2026-11-03' or value.get('source_bound') is not False:
        raise ReleaseError(f'Not an unresolved, observed proposal: {path}')
    for effect in ('accepted_coverage_effect', 'accepted_evidence_effect'):
        if value.get(effect) != 'NONE':
            raise ReleaseError(f'Proposal falsely claims admission: {path}')
    return value, _digest(_raw(path))


def _edition_crosswalk(item: dict, row: dict, observations: dict) -> str:
    """Exact edition-page crosswalk; never reconcile global Work identities."""
    work = item['candidate_work_id']
    editions = [v for v in observations['records'] if v.get('candidate_work_id') == work]
    source_url = row['source_locator']
    evidence_url = item['source_locator']
    matches = {v['publisher_url']: v for v in editions}
    if source_url not in matches or evidence_url not in matches:
        raise ReleaseError(f'Publisher observation has no paired source+evidence edition: {work}')
    source_ed, evidence_ed = matches[source_url], matches[evidence_url]
    if any(source_ed[k] != evidence_ed[k] for k in ('candidate_work_id', 'title', 'creator')):
        raise ReleaseError(f'Edition title or creator divergence: {work}')
    if source_ed['title'] != row['title']:
        raise ReleaseError(f'Directory title not same local candidate: {work}')
    for edition in (source_ed, evidence_ed):
        if not isinstance(edition.get('isbn13'), str) or not edition['isbn13'].isdigit() or len(edition['isbn13']) != 13:
            raise ReleaseError(f'Invalid edition ISBN: {work}')
        parsed = _url(edition['publisher_url'], 'www.simonandschuster.com')
        if parsed.rsplit('/', 1)[-1] != edition['isbn13']:
            raise ReleaseError(f'ISBN not bound to publisher edition URL: {work}')
    left, right = urlsplit(source_url).path.rsplit('/', 1)[0], urlsplit(evidence_url).path.rsplit('/', 1)[0]
    if left != right:
        raise ReleaseError(f'Different publisher title family, not an edition crosswalk: {work}')
    return f"row ISBN {source_ed['isbn13']}; description-edition ISBN {evidence_ed['isbn13']}"


def candidate_entries() -> list[dict]:
    directory = _load('explorer/discovery-catalog.json')
    film_catalog = _load('explorer/film-catalog.json')
    rows = {r['row_id']: r for r in directory['rows']}
    films = {r['id']: r for r in film_catalog['films']}
    if len(rows) != 1214 or len(films) != 14:
        raise ReleaseError('Source-local directory count or film catalog drifted')
    entries = []
    for path in OBSERVATIONS:
        data, sha = _source_artifact(path)
        if 'work_synopses' in data:
            if data.get('full_text_read') is not False:
                raise ReleaseError('Publisher blurb mistaken for book reading')
            for synopsis in data['work_synopses']:
                candidate = synopsis['candidate_work_id']
                row = rows.get(f'literature:{candidate}')
                if not row or row['medium'] != 'LITERATURE' or synopsis.get('status') != 'PUBLISHER_DESCRIPTION_PARAPHRASE':
                    raise ReleaseError(f'No literature source-local row for {candidate}')
                if row['source_group'] not in ('publisher:simonandschuster.com', 'distributor:penguinrandomhouse.com:titan-books'):
                    raise ReleaseError('Literary source is not direct publisher/distributor metadata')
                if row['source_group'].startswith('publisher:'):
                    crosswalk = _edition_crosswalk(synopsis, row, data)
                else:
                    matching = [r for r in data['records'] if r['candidate_work_id'] == candidate]
                    if len(matching) != 1 or matching[0]['publisher_url'] != row['source_locator'] or synopsis['source_locator'] != row['source_locator']:
                        raise ReleaseError(f'PRH edition locator mismatch: {candidate}')
                    _url(row['source_locator'], 'www.penguinrandomhouse.com')
                    crosswalk = f"row ISBN {matching[0]['isbn13']}; same publisher description URL"
                entry = {
                    'row_id': f'directory:{row["row_id"]}', 'title': row['title'], 'medium': 'LITERATURE',
                    'source_group': row['source_group'], 'source_input': row['source_input'],
                    'source_context': row['context'], 'source_locator': row['source_locator'],
                    'overview_evidence_locator': synopsis['source_locator'],
                    'overview_text': _clean_synopsis(synopsis['synopsis']),
                    'overview_basis': 'PUBLISHER_DESCRIPTION_PARAPHRASE',
                    'source_snapshot_date': data['observed_on_utc'],
                    'research_observation_path': path, 'research_observation_sha256': sha,
                    'raw_webpage_sha256': None, 'editorial_receipt_sha256': None,
                    'directory_alias_row_id': None, 'directory_alias_context': None,
                    'admission_effect': 'NONE', 'coverage_effect': 'NONE',
                    'candidate_work_id': candidate, 'edition_crosswalk': crosswalk,
                }
                entries.append(entry)
        else:
            if data.get('raw_source_page_sha256') is not None or data.get('full_film_viewed') is not False:
                raise ReleaseError('Movie publisher summary falsely claims viewed source or raw byte custody')
            for synopsis in data['records']:
                row = rows.get(synopsis['directory_row_id'])
                film = films.get(synopsis['candidate_film_id'])
                if not row or not film or row['medium'] != 'FILM' or synopsis.get('status') != 'PUBLISHER_DESCRIPTION_PARAPHRASE':
                    raise ReleaseError('Film has no exact source-local observation')
                if row['source_locator'] != synopsis['source_locator'] or film['source_locator'] != synopsis['source_locator'] or row['title'] != synopsis['title'] or film['title'] != synopsis['title']:
                    raise ReleaseError('Film directory/candidate/studio source mismatch')
                if row['source_group'] != film['source_group'] or row['source_input'] != 'explorer/film-catalog.json' or row['context'] != 'Star Trek films':
                    raise ReleaseError('Film directory cannot be safely cross-displayed as the identical source observation')
                _url(row['source_locator'], 'www.startrek.com')
                entries.append({
                    'row_id': f'film:{film["id"]}', 'title': row['title'], 'medium': 'FILM',
                    'source_group': film['source_group'], 'source_input': 'explorer/film-catalog.json',
                    'source_context': film['work_type'], 'source_locator': film['source_locator'],
                    'overview_evidence_locator': synopsis['source_locator'],
                    'overview_text': _clean_synopsis(synopsis['synopsis']),
                    'overview_basis': 'PUBLISHER_DESCRIPTION_PARAPHRASE',
                    'source_snapshot_date': data['observed_on_utc'],
                    'research_observation_path': path, 'research_observation_sha256': sha,
                    'raw_webpage_sha256': None, 'editorial_receipt_sha256': None,
                    'directory_alias_row_id': f'directory:{row["row_id"]}',
                    'directory_alias_context': row['context'],
                    'admission_effect': 'NONE', 'coverage_effect': 'NONE',
                    'candidate_work_id': synopsis['candidate_film_id'], 'edition_crosswalk': 'same studio source locator',
                })
    ids = [r['row_id'] for r in entries]
    if len(ids) != 23 or len(set(ids)) != 23 or sum(r['medium'] == 'LITERATURE' for r in entries) != 9:
        raise ReleaseError(f'Wrong exact publisher synopsis set: {len(ids)}')
    return sorted(entries, key=lambda r: r['row_id'])


def review_request(candidates: list[dict]) -> dict:
    return {
        'schema_version': '1.0.0', 'review_state': 'REQUIRES_INDEPENDENT_EDITORIAL_REVIEW',
        'source_kind': 'OFFICIAL_RENDERED_PUBLISHER_DESCRIPTION_PARAPHRASE',
        'raw_webpage_sha256': None, 'coverage_effect': 'NONE', 'admission_effect': 'NONE',
        'entry_count': len(candidates),
        'entries': [{k: entry[k] for k in ('row_id', 'title', 'medium', 'source_group', 'source_locator',
                                         'overview_evidence_locator', 'source_snapshot_date',
                                         'research_observation_path', 'research_observation_sha256',
                                         'candidate_work_id', 'edition_crosswalk',
                                         'directory_alias_row_id', 'directory_alias_context')} | {
                                             'original_paraphrase_sha256': _text_fingerprint(entry['overview_text'])
                                         } for entry in candidates],
    }


def public_release(candidates: list[dict], editorial: dict, request: dict) -> dict:
    keys = {'schema_version', 'review_kind', 'review_result', 'reviewed_on_utc', 'reviewer_agent', 'provider',
            'runtime', 'review_independence', 'review_request_sha256', 'accepted_observation_commit',
            'source_artifacts', 'reviewed_paraphrase_count', 'passed_paraphrase_count',
            'failed_paraphrase_count', 'source_review_method', 'reviewed_paraphrases',
            'material_qualifications', 'source_admission_effect', 'work_admission_effect',
            'evidence_admission_effect', 'coverage_effect', 'artwork_release_effect', 'site_release_effect'}
    required_artifacts = sorted((path, _digest(_raw(path)),
                                 sum(c['research_observation_path'] == path for c in candidates)) for path in OBSERVATIONS)
    actual_artifacts = sorted((a['path'], a['sha256'], a['reviewed_paraphrases']) for a in editorial.get('source_artifacts', [])
                              if isinstance(a, dict) and {'path', 'sha256', 'reviewed_paraphrases'} <= set(a))
    required_texts = sorted((entry['row_id'], _text_fingerprint(entry['overview_text'])) for entry in candidates)
    reviewed_texts = editorial.get('reviewed_paraphrases')
    if set(editorial) != keys or editorial.get('schema_version') != '1.0.0' or \
       editorial.get('review_kind') != 'MODEL_EDITORIAL_REVIEW' or \
       editorial.get('review_result') != 'PASS_23_SOURCE_LABELED_PROMOTIONAL_PARAPHRASES_ONLY' or \
       editorial.get('reviewer_agent') != '/root/repo_workflow_merger_audit' or \
       editorial.get('provider') != 'OpenAI' or \
       editorial.get('runtime') != 'ChatGPT native subagent (model identity not externally attested)' or \
       editorial.get('review_independence') != 'SEPARATE_MODEL_AGENT_FROM_CANDIDATE_AND_RELEASE_AUTHORS' or \
       editorial.get('review_request_sha256') != _digest(_pretty(request)) or \
       editorial.get('accepted_observation_commit') != '61c9bd6419e60e8800c4462d023def868f711ccd' or \
       actual_artifacts != required_artifacts or len(editorial.get('source_artifacts', [])) != len(OBSERVATIONS) or \
       editorial.get('reviewed_paraphrase_count') != len(candidates) or \
       editorial.get('passed_paraphrase_count') != len(candidates) or \
       editorial.get('failed_paraphrase_count') != 0 or \
       not isinstance(reviewed_texts, list) or sorted(map(tuple, reviewed_texts)) != required_texts or \
       any(editorial.get(k) != 'NONE' for k in ('source_admission_effect', 'work_admission_effect',
                                                 'evidence_admission_effect', 'coverage_effect',
                                                 'artwork_release_effect', 'site_release_effect')):
        raise ReleaseError('No exact separately authored MODEL editorial review receipt for source/text tuples')
    receipt_hash = _digest(_raw(REVIEW_PATH))
    clean = []
    for entry in candidates:
        row = {key: value for key, value in entry.items() if key not in ('candidate_work_id', 'edition_crosswalk')}
        row['editorial_receipt_sha256'] = receipt_hash
        clean.append(row)
    return {
        'schema_version': '1.0.0', 'data_status': 'EDITORIALLY_REVIEWED_DISPLAY_ONLY',
        'coverage_effect': 'NONE', 'admission_effect': 'NONE',
        'synopsis_count': len(clean), 'synopses': clean,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--review-request', action='store_true', help='Generate/update proposal-only editorial review request')
    parser.add_argument('--check', action='store_true', help='Compare already accepted public sidecar to generated output')
    args = parser.parse_args()
    candidates = candidate_entries()
    request = review_request(candidates)
    if args.review_request:
        target = ROOT / REQUEST_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_pretty(request))
        print(f'EDITORIAL_REQUEST_OK: {len(candidates)} proposed publisher overview tuples; NOT released')
        return
    if _raw(REQUEST_PATH) != _pretty(request):
        raise ReleaseError('Review request does not exactly match current accepted source observations')
    artifact = public_release(candidates, _load(REVIEW_PATH), request)
    output = _pretty(artifact)
    if args.check:
        if _raw(PUBLIC_PATH) != output:
            raise ReleaseError('Published synopsis sidecar is stale or manually edited')
        print(f'PUBLISHER_SYNOPSIS_RELEASE_OK: {len(candidates)} model-reviewed publisher overviews, no admitted Works')
    else:
        target = ROOT / PUBLIC_PATH
        target.write_bytes(output)
        print(f'PUBLISHER_SYNOPSIS_GENERATED: {len(candidates)} separately model-reviewed publisher overviews')


if __name__ == '__main__':
    main()
