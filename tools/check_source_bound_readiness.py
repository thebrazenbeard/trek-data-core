#!/usr/bin/env python3
"""Read-only preflight for a *proposed* first nonfixture SOURCE_BOUND event.

This is not a source-admission tool. A declared hash is insufficient: readiness
requires replaying an exact local byte-custody receipt against actual bytes,
then checking accepted Librarian records and an accepted DISCOVERED predecessor.
The result cannot attest to provenance, rights, Work identity or human review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import coverage_ledger as ledger
import source_custody_receipt as custody

ROOT = Path(__file__).resolve().parents[1]


def assess(work_id, source_id, binding_id, works, sources, bindings, records,
           request_path=None, receipt_path=None, source_file=None):
    """Only deterministic prerequisite checks; never constructs a coverage event."""
    blockers = []
    work = works.get(work_id)
    source = sources.get(source_id)
    binding = bindings.get(binding_id)

    # Caller-provided roster indexes are not evidence that the indexed rows
    # actually identify the requested Work, Source, or binding.
    if work is not None and work.get('work_id') != work_id:
        blockers.append('WORK_IDENTITY_MISMATCH')
    if source is not None and source.get('source_id') != source_id:
        blockers.append('SOURCE_IDENTITY_MISMATCH')
    if binding is not None and binding.get('binding_id') != binding_id:
        blockers.append('BINDING_IDENTITY_MISMATCH')

    if not work or work.get('status') != 'ACCEPTED' or work.get('fixture_only') is not False:
        blockers.append('NO_ACCEPTED_NONFIXTURE_WORK')
    elif work.get('work_type') != 'EPISODE':
        blockers.append('WORK_NOT_EPISODE')
    if not source or source.get('status') != 'ACCEPTED' or source.get('fixture_only') is not False:
        blockers.append('NO_ACCEPTED_NONFIXTURE_SOURCE')
    if not binding or binding.get('lifecycle') != 'ACCEPTED' or binding.get('fixture_only') is not False:
        blockers.append('NO_ACCEPTED_NONFIXTURE_BINDING')
    else:
        if binding.get('work_id') != work_id or binding.get('source_id') != source_id:
            blockers.append('BINDING_CONTEXT_MISMATCH')
        if binding.get('mapping_role') != 'EVIDENCE_BEARING' or not str(binding.get('method') or '').strip():
            blockers.append('NOT_EVIDENCE_BEARING_BINDING')
        if not source or not ledger.accepted_source_binding_basis(source, binding):
            blockers.append('NO_EXACT_SOURCE_BYTE_HASH_BASIS')
        if any(b.get('lifecycle') == 'ACCEPTED' and b.get('supersedes_binding_id') == binding_id
               for b in bindings.values()):
            blockers.append('BINDING_SUPERSEDED')

    active = ledger.active_events(ledger.index_records(records, 'coverage_event', 'coverage_event_id'))
    discovered = sorted(eid for eid, row in active.items()
                        if row.get('status') == 'ACCEPTED' and row.get('effect') == 'ATTAINED'
                        and row.get('coverage_state') == 'DISCOVERED'
                        and row.get('work_id') == work_id and row.get('subject_type') == 'WORK'
                        and row.get('subject_id') == work_id and row.get('producer_role') == 'LIBRARIAN')
    if not discovered:
        blockers.append('NO_ACCEPTED_DISCOVERED_PREDECESSOR')
    already_bound = sorted(eid for eid, row in active.items()
                           if row.get('status') == 'ACCEPTED' and row.get('effect') == 'ATTAINED'
                           and row.get('coverage_state') == 'SOURCE_BOUND'
                           and row.get('work_id') == work_id and row.get('source_id') == source_id
                           and row.get('binding_id') == binding_id)
    if already_bound:
        blockers.append('SOURCE_BOUND_ALREADY_ATTAINED')

    supplied = [request_path is not None, receipt_path is not None, source_file is not None]
    if not all(supplied):
        blockers.append('EXACT_PRIVATE_BYTE_CUSTODY_NOT_SUPPLIED' if not any(supplied)
                        else 'INCOMPLETE_BYTE_CUSTODY_INPUTS')
    else:
        try:
            request = custody.read_json(Path(request_path))
            observed = custody.read_json(Path(receipt_path))
            verified = custody.build_receipt(request, Path(source_file))
            if observed != verified:
                raise custody.Rejected('receipt does not replay against exact local source bytes')
            if source is None:
                raise custody.Rejected('no accepted Source to compare with byte receipt')
            expected = {
                'source_candidate_id': source_id,
                'source_kind': source.get('source_kind'),
                'source_locator': source.get('locator'),
                'source_version': source.get('source_version'),
                'provenance_family': source.get('provenance_family'),
                'independence_group': source.get('independence_group'),
                'content_sha256': str(source.get('content_hash') or '').removeprefix('sha256:'),
            }
            if any(verified.get(key) != value for key, value in expected.items()):
                raise custody.Rejected('custody receipt does not match exact accepted Source identity/hash')
        except (custody.Rejected, OSError, ValueError, TypeError):
            blockers.append('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED')

    blockers = sorted(set(blockers))
    return {
        'schema_version': '1.0.0',
        'report_kind': 'SOURCE_BOUND_EVENT_PREFLIGHT_NOT_ADMISSION',
        'status': 'READY_FOR_EVENT_PROPOSAL_REVIEW_REQUIRED' if not blockers else 'BLOCKED',
        'work_id': work_id, 'source_id': source_id, 'binding_id': binding_id,
        'accepted_discovered_event_ids': discovered,
        'blockers': blockers,
        'source_bytes_republished': False,
        'coverage_event_created': False,
        'coverage_effect': 'NONE',
        'rights_identity_and_independent_review': 'NOT_ESTABLISHED_BY_THIS_REPORT',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-id', required=True)
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--binding-id', required=True)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--source-file', type=Path)
    parser.add_argument('--require-ready', action='store_true')
    args = parser.parse_args(argv)

    # No prerequisite can be green when globally governed inputs are invalid.
    for script, command in (('validate.py', []), ('coverage_ledger.py', ['validate'])):
        run = subprocess.run([sys.executable, str(ROOT / 'tools' / script), *command],
                             cwd=ROOT, capture_output=True, text=True, check=False)
        if run.returncode:
            print(json.dumps({'status': 'INVALID_GOVERNED_INPUT', 'validator': script,
                              'coverage_effect': 'NONE'}, sort_keys=True))
            return 3
    try:
        records, paths = ledger.scan_typed_records(with_paths=True)
        if ledger.validate_coverage(records, record_paths=paths, enforce_origins=True):
            raise ValueError('invalid coverage origin')
        result = assess(args.work_id, args.source_id, args.binding_id,
                        ledger.authoritative_work_roster(),
                        *ledger.authoritative_source_binding_rosters(), records,
                        args.request, args.receipt, args.source_file)
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({'status': 'INVALID_GOVERNED_INPUT', 'coverage_effect': 'NONE'}, sort_keys=True))
        return 3
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if args.require_ready and result['status'] == 'BLOCKED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
