# Voyager working batch voy-s01-b003

Scope: `Heroes and Demons`, `Cathexis`, `Faces`, `Jetrel`, `Learning Curve`.

Status: **working extraction complete; accepted source/work binding blocked**.

This branch is based directly on accepted `main` commit
`d58359a207da89e812d0a0330558c66774ed1241`. It does not depend on the
provisional b001 or b002 branches and does not advance accepted coverage.

## Source handling

Each work was processed from the complete available Springfield! Springfield!
episode-script rendering recorded in `source-read-log.jsonl`. These are treated
as secondary complete-transcript representations, not as authoritative
audiovisual masters, production teleplays, or accepted Trek source bindings.
No copyrighted transcript text is committed here.

Source hashes remain null because the Librarian has not supplied accepted
source instances/hashes. Fabricating a hash would be prettier and useless.

## Research handling

Records use work-local entities and source-relative evidence. In particular:

- `Heroes and Demons`: photonic life-forms and holodeck characters remain
  frame-scoped; the missing crew's exact photonic conversion mechanism stays
  unresolved.
- `Cathexis`: Chakotay's supported body and displaced consciousness are
  represented separately inside the work without a global body/mind ontology.
- `Faces`: pre-split Torres, human-derived and Klingon-derived counterparts,
  and post-reintegration Torres are local states/counterparts. Biological
  reintegration does not silently assert merger of consciousness.
- `Jetrel`: Neelix's earlier military-service claim and Jetrel's medical claim
  are preserved and then superseded/contradicted by later testimony. The
  failed regenerative-fusion attempt creates no restored-person entity.
- `Learning Curve`: Starfleet/Maquis institutional tension is coded as
  reciprocal adaptation rather than assuming one rule system is inherently
  correct.

## Blockers

- accepted Voyager Work IDs are absent on `main`;
- accepted Source IDs and hashes are absent on `main`;
- accepted schema and predicate registry are absent on `main`.

Until those exist, the batch is not projection-eligible and does not advance
accepted Voyager coverage.
