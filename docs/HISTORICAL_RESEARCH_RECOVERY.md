# Historical research recovery: proposal inventory, not admission

Older Trek Research chats and branch names refer to many researched episode
batches. They are not trustworthy evidence that those episodes reached
accepted `main`. Historical PR heads may contain unique `research/` files,
including incompatible versions of the same path, and the old tree also
contained a hazardous editor `folderOpen` startup task.

The offline inventory tool exists to **locate candidates without running
historical code or promoting a single claim**.

## Safe snapshot workflow

1. Use a **disposable audit clone** only. Populate isolated PR-head refs by
   following [the branch census ref layout](BRANCH_CENSUS_REF_NAMESPACES.md).
   Do not fetch the snapshot into an active collaborator's checkout. Do not
   open untrusted old heads in an editor or run their scripts, hooks or tasks.
2. Pin the exact accepted `main` SHA from the collected clone and run:

   ```bash
   python3 tools/inventory_historical_research.py \
     --repo /path/to/disposable-audit-clone \
     --expected-main-sha EXACT_FULL_MAIN_SHA
   ```

   Redirect stdout into a protected review record if persistence is needed.
   The command is read-only: it uses `rev-parse`, `for-each-ref` and
   `ls-tree -r -z`, with lazy fetching disabled. It requires isolated numeric
   `refs/trek-audit/pr-heads/` refs and fails if they are absent or `main`
   differs from the pinned commit.
3. Review `paths[].versions` in the JSON report. Each proposal carries its
   Git **object ID**, mode, type and PR-head numbers. Multiple different
   objects at one path are retained as conflicts. A `same_bytes_on_main`
   flag means only that Git tree identity agrees, not that evidence was
   independently checked. `unsafe_object_mode` marks executable-mode files,
   symlinks and submodules so they cannot silently disappear from review.
4. Open and evaluate selected records **as inert text/data** in an isolated
   evidence review process. Separately check source locator, rights basis,
   actual source version/digest, Source↔Work identity, observations, assertions
   and conflicts under the [research method](../TREK_RESEARCH_METHOD.md).
   Resolve path collisions without discarding historical variants. Only
   after independent admission may a reviewed batch enter canonical records.

## What the receipt proves—and does not

`manifest_sha256` hashes the JSON report without that field, using sorted
keys and compact UTF-8 JSON. It makes two inventory outputs comparable for
the exact recorded Git object IDs and ref names. Git blob IDs identify Git
objects; **they are not independent checksums of audiovisual source bytes**.

Every report declares `UNTRUSTED_HISTORICAL_PROPOSALS`, with admission,
acceptance, coverage and denominator effects of `NONE`. The tool does not
read historical blobs, establish genuine episode identity, resolve Works,
verify an episode was watched, approve projection hashes, create coverage
events, delete branches, merge or deploy.

Test the parser against synthetic snapshots:

```bash
python3 -m unittest discover -s tests -p 'test_inventory_historical_research.py' -v
```
