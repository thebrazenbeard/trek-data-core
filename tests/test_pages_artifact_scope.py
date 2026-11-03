"""Source-only safety checks for the public Pages artifact boundary."""

import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "static.yml"


def job_body(name: str) -> str:
    """Return one precisely delimited Actions job by two-space indentation."""
    source = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [a-z][a-z0-9_-]*:\n|\Z)",
        source.split("\njobs:\n", 1)[1],
    )
    if match is None:
        raise AssertionError(f"missing job {name}")
    return match.group(1)


def workflow_step(name: str) -> str:
    """Extract the exact bash body of a workflow step for a runtime test."""
    rows = WORKFLOW.read_text(encoding="utf-8").splitlines()
    header = f"      - name: {name}"
    if header not in rows:
        raise AssertionError(f"missing step: {name}")
    start = rows.index(header)
    run_line = next(i for i in range(start + 1, len(rows)) if rows[i] == "        run: |")
    body = []
    for row in rows[run_line + 1:]:
        if row.startswith("      - name:") or row.startswith("  deploy:"):
            break
        if row.strip():
            if not row.startswith("          "):
                raise AssertionError(f"malformed script indentation: {row}")
            body.append(row[10:])
        else:
            body.append("")
    return "\n".join(body)


class PagesArtifactScopeTests(unittest.TestCase):
    def test_browser_assets_use_exact_content_hash_cache_versions(self):
        """A stale browser cache must not pair old JS/CSS with a new index."""
        html = (ROOT / "explorer" / "index.html").read_text(encoding="utf-8")
        for name in ("app.js", "app.css", "trek-data-core-hero.jpg"):
            digest = hashlib.sha256((ROOT / "explorer" / name).read_bytes()).hexdigest()
            self.assertIn(f'./{name}?v={digest}', html, name)

    def test_artifact_is_only_the_explorer_directory(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: explorer", text)
        self.assertNotIn("path: '.'", text)
        self.assertNotIn('path: "."', text)

    def test_requires_index_and_entrypoint(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test -f explorer/index.html", text)
        self.assertIn("test -f explorer/index.json", text)
        self.assertIn("test -f explorer/trek-data-core-hero.jpg", text)

    def test_drops_unfinished_template_steps(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("actions/cache@", text)
        self.assertNotIn("actions/setup-dotnet@", text)
        self.assertIn("actions/upload-pages-artifact@7b1f4a764d45c48632c6b24a0339c27f5614fb0b", text)

    def test_external_actions_are_pinned_to_immutable_commit_ids(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        actions = re.findall(r"(?m)^\s+uses:\s+(actions/[\w-]+)@([^\s#]+)", text)
        expected = {
            "actions/checkout": "d23441a48e516b6c34aea4fa41551a30e30af803",
            "actions/upload-pages-artifact": "7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
            "actions/deploy-pages": "368f82528645a54fb793d4d04e342629a3f51346",
        }
        self.assertEqual(dict(actions), expected)
        self.assertEqual(len(actions), len(expected))

    def test_publication_requires_explicit_manual_dispatch(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        header = source.split("\njobs:\n", 1)[0]
        events = header.split("\non:\n", 1)[1].split("\nconcurrency:\n", 1)[0]
        meaningful = [line.strip() for line in events.splitlines()
                      if line.strip() and not line.strip().startswith("#")]
        self.assertEqual(meaningful, ["workflow_dispatch:"])
        self.assertNotRegex(source, r"(?m)^  (?:push|pull_request|schedule|workflow_run|repository_dispatch):")

    def test_catalog_index_still_verified_before_manual_release(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python3 tools/build_explorer_index.py", text)
        self.assertIn('cmp "${RUNNER_TEMP}/trek-index-expected.json" explorer/index.json', text)

    def test_deployment_gates_on_behavior_and_exact_allowlist(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", text)
        self.assertIn("node tests/test_explorer.mjs", text)
        self.assertIn("python3 -m unittest discover", text)
        self.assertIn("! -path explorer/app.js", text)
        self.assertIn("! -path explorer/app.css", text)
        self.assertIn("! -path explorer/trek-data-core-hero.jpg", text)
        self.assertIn("! -path explorer/research-leads.json", text)
        self.assertIn("! -path explorer/film-catalog.json", text)
        self.assertIn("! -path explorer/discovery-catalog.json", text)
        self.assertIn("! -path explorer/synopsis-catalog.json", text)
        self.assertIn("Refusing to publish an unexpected Explorer entry", text)

    def test_manual_dispatch_cannot_deploy_a_review_branch(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: github.ref == 'refs/heads/main'", text)
        self.assertIn("if: needs.build.outputs.ready == 'true' && github.ref == 'refs/heads/main'", text)

    def test_pages_can_land_first_without_publishing_missing_explorer(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("id: readiness", text)
        self.assertIn("ready=false", text)
        self.assertIn("skipping Pages publication", text)
        self.assertEqual(text.count("if: steps.readiness.outputs.ready == 'true'"), 8)
        self.assertIn("ready: ${{ steps.readiness.outputs.ready }}", job_body("build"))
        self.assertIn("needs: build", job_body("deploy"))

    def test_build_has_read_only_token_and_no_ambient_deployment_privileges(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        header = source.split("\njobs:\n", 1)[0]
        # Permissions inherited at workflow level must not grant elevated
        # OIDC or Pages tokens to repository test and build steps.
        self.assertNotIn("permissions:", header)
        build = job_body("build")
        self.assertRegex(build, r"(?m)^    permissions:\n      contents: read$")
        self.assertNotIn("pages: write", build)
        self.assertNotIn("id-token: write", build)
        self.assertIn("actions/checkout@", build)
        self.assertIn("persist-credentials: false", build)
        self.assertIn("python3 -m unittest discover", build)
        self.assertIn("node tests/test_explorer.mjs", build)
        self.assertIn("python3 tools/build_explorer_index.py", build)
        self.assertIn("actions/upload-pages-artifact@7b1f4a764d45c48632c6b24a0339c27f5614fb0b", build)
        self.assertNotIn("actions/deploy-pages@", build)
        self.assertIn("python3 tools/build_research_leads.py --check", build)

    def test_privileged_deploy_job_runs_no_repo_code(self):
        deploy = job_body("deploy")
        self.assertRegex(deploy, r"(?m)^    permissions:\n      pages: write\n      id-token: write$")
        self.assertIn("needs: build", deploy)
        self.assertIn("if: needs.build.outputs.ready == 'true'", deploy)
        self.assertIn("uses: actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346", deploy)
        self.assertNotIn("actions/checkout@", deploy)
        self.assertNotIn("actions/upload-pages-artifact@", deploy)
        self.assertNotIn("actions/configure-pages@", deploy)
        self.assertNotIn("run:", deploy)
        self.assertNotIn("python3", deploy)
        self.assertNotIn("node ", deploy)
        self.assertNotIn("contents: read", deploy)
        self.assertEqual(deploy.count("uses:"), 1)

    def test_final_integrity_barrier_runs_after_every_repo_command(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertLess(text.index("Verify Explorer behavior before deployment"),
                        text.index("Verify deterministic catalog index"))
        self.assertLess(text.index("Verify deterministic catalog index"),
                        text.index("Verify optional Research Leads index"))
        self.assertLess(text.index("Verify optional Research Leads index"),
                        text.index("Verify optional Film discovery index"))
        self.assertLess(text.index("Verify optional Film discovery index"),
                        text.index("Verify optional Multimedia discovery directory"))
        self.assertLess(text.index("Verify optional Multimedia discovery directory"),
                        text.index("Verify optional publisher-description synopsis release"))
        self.assertLess(text.index("Verify optional publisher-description synopsis release"),
                        text.index("Verify final public artifact boundary"))
        self.assertLess(text.index("Verify final public artifact boundary"),
                        text.index("Upload Explorer only"))
        self.assertIn('cmp "${RUNNER_TEMP}/trek-index-expected.json" explorer/index.json', text)
        final = workflow_step("Verify final public artifact boundary")
        self.assertIn('git rev-parse "HEAD:$path"', final)
        self.assertIn('git hash-object "$path"', final)
        self.assertIn("Refusing to publish an unexpected Explorer entry", final)
        self.assertIn("find explorer -mindepth 1", final)
        self.assertIn("git rev-parse HEAD:explorer/research-leads.json", final)
        self.assertIn("git rev-parse HEAD:explorer/film-catalog.json", final)
        self.assertIn("git rev-parse HEAD:explorer/discovery-catalog.json", final)
        self.assertIn("git rev-parse HEAD:explorer/synopsis-catalog.json", final)
        self.assertIn("cmp docs/assets/trek-data-core-hero.jpg explorer/trek-data-core-hero.jpg", final)

    def test_final_barrier_rejects_post_test_modifications_and_new_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            explorer = root / "explorer"
            explorer.mkdir()
            for name in ("index.html", "index.json", "app.js", "app.css", "trek-data-core-hero.jpg"):
                (explorer / name).write_text("accepted bytes\n", encoding="utf-8")
            art = root / "docs/assets"
            art.mkdir(parents=True)
            (art / "trek-data-core-hero.jpg").write_text("accepted bytes\n", encoding="utf-8")
            for command in (
                ["git", "init", "-q"],
                ["git", "add", "--", "explorer"],
                ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Accepted Explorer fixture"],
            ):
                result = subprocess.run(command, cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

            script = workflow_step("Verify final public artifact boundary")

            def check():
                return subprocess.run(
                    ["bash", "-e", "-u", "-o", "pipefail", "-c", script],
                    cwd=root, capture_output=True, text=True,
                )

            self.assertEqual(check().returncode, 0)
            (explorer / "app.js").write_text("mutated after unit tests\n", encoding="utf-8")
            self.assertNotEqual(check().returncode, 0)
            (explorer / "app.js").write_text("accepted bytes\n", encoding="utf-8")
            self.assertEqual(check().returncode, 0)
            (explorer / "secret.txt").write_text("unexpected\n", encoding="utf-8")
            self.assertNotEqual(check().returncode, 0)
            (explorer / "secret.txt").unlink()
            (explorer / "app.js").unlink()
            (explorer / "app.js").symlink_to("index.html")
            self.assertNotEqual(check().returncode, 0)

    def test_manual_dispatch_without_complete_explorer_is_a_noop(self):
        readiness = workflow_step("Check whether the Explorer has landed on main")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "github-output"
            env = {**os.environ, "GITHUB_OUTPUT": str(output)}

            def check():
                return subprocess.run(
                    ["bash", "-e", "-u", "-o", "pipefail", "-c", readiness],
                    cwd=root, env=env, capture_output=True, text=True,
                )

            missing = check()
            self.assertEqual(missing.returncode, 0, missing.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "ready=false\n")
            self.assertIn("skipping Pages publication", missing.stdout)

            explorer = root / "explorer"
            explorer.mkdir()
            for name in ("index.html", "index.json", "app.js", "app.css", "trek-data-core-hero.jpg"):
                (explorer / name).write_text("fixture\n", encoding="utf-8")
            output.unlink()
            ready = check()
            self.assertEqual(ready.returncode, 0, ready.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "ready=true\n")

    def fixture(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        explorer = root / "explorer"
        explorer.mkdir()
        for name in ("index.html", "index.json", "app.js", "app.css", "trek-data-core-hero.jpg"):
            (explorer / name).write_text("verified\n", encoding="utf-8")
        art = root / "docs/assets"
        art.mkdir(parents=True)
        (art / "trek-data-core-hero.jpg").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(root)
        return root

    def commit_fixture(self, root: Path) -> None:
        if not (root / ".git").exists():
            init = subprocess.run(["git", "init", "-q"], cwd=root, capture_output=True, text=True)
            self.assertEqual(init.returncode, 0, init.stderr)
        for command in (
            ["git", "add", "--", "explorer", "docs/assets/trek-data-core-hero.jpg"],
            ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "commit", "-qm", "Accepted Explorer fixture"],
        ):
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def check_step(self, name: str, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "-e", "-u", "-o", "pipefail", "-c", workflow_step(name)],
            cwd=root, capture_output=True, text=True,
        )

    def test_five_file_release_needs_no_research_generator(self):
        root = self.fixture()
        self.assertEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.assertFalse((root / "tools/build_research_leads.py").exists())

    def test_sixth_research_file_without_generator_fails_closed(self):
        root = self.fixture()
        (root / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(root)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.assertNotEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)

    def test_sixth_research_file_must_be_committed_and_byte_identical(self):
        root = self.fixture()
        fifth = root / "explorer/research-leads.json"
        fifth.write_text("unreviewed\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.commit_fixture(root)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        fifth.write_text("modified after tests\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        fifth.unlink()
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)

    def test_sixth_research_file_runs_actual_check_command_and_propagates_failures(self):
        root = self.fixture()
        (root / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(root)
        tool = root / "tools/build_research_leads.py"
        tool.parent.mkdir()
        # A synthetic verifier proves the workflow runs --check and fails closed.
        tool.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "assert sys.argv[1:] == ['--check']\n"
            "assert Path('proposals/discovery/candidates.ready').is_file()\n"
            "assert Path('explorer/research-leads.json').read_bytes() == b'verified\\n'\n",
            encoding="utf-8",
        )
        self.assertNotEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)
        (root / "proposals/discovery").mkdir(parents=True)
        (root / "proposals/discovery/candidates.ready").touch()
        self.assertEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        (root / "explorer/research-leads.json").write_text("tampered\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)

    def test_film_index_requires_committed_unchanged_bytes(self):
        root = self.fixture()
        output = root / "explorer/film-catalog.json"
        output.write_text("discovery\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.commit_fixture(root)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.write_text("tampered after tests\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.write_text("discovery\n", encoding="utf-8")
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.unlink()
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)

    def test_film_index_and_generator_symlinks_are_refused(self):
        root = self.fixture()
        output = root / "explorer/film-catalog.json"
        output.symlink_to("index.json")
        self.assertNotEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.unlink()
        output.write_text("discovery\n", encoding="utf-8")
        self.commit_fixture(root)
        tool = root / "tools/build_film_catalog.py"
        tool.parent.mkdir()
        (tool.parent / "other.py").write_text("print('ok')\n", encoding="utf-8")
        tool.symlink_to("other.py")
        self.assertNotEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)

    def test_optional_film_generator_must_exist_and_pass_its_check(self):
        root = self.fixture()
        output = root / "explorer/film-catalog.json"
        output.write_text("discovery\n", encoding="utf-8")
        self.commit_fixture(root)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.assertNotEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)
        tool = root / "tools/build_film_catalog.py"
        tool.parent.mkdir()
        tool.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "assert sys.argv[1:] == ['--check']\n"
            "assert Path('proposals/film.ready').exists()\n"
            "assert Path('explorer/film-catalog.json').read_bytes() == b'discovery\\n'\n",
            encoding="utf-8",
        )
        self.assertNotEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)
        (root / "proposals").mkdir()
        (root / "proposals/film.ready").touch()
        self.assertEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)
        output.write_text("modified\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify optional Film discovery index", root).returncode, 0)

    def test_unified_directory_requires_committed_unchanged_bytes(self):
        root = self.fixture()
        output = root / "explorer/discovery-catalog.json"
        output.write_text("source-only\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        self.commit_fixture(root)
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.write_text("tampered\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.unlink()
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)

    def test_unified_directory_generator_and_symlinks_fail_closed(self):
        root = self.fixture()
        output = root / "explorer/discovery-catalog.json"
        output.symlink_to("index.json")
        self.assertNotEqual(self.check_step("Verify optional Multimedia discovery directory", root).returncode, 0)
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        output.unlink()
        output.write_text("source-only\n", encoding="utf-8")
        self.commit_fixture(root)
        self.assertNotEqual(self.check_step("Verify optional Multimedia discovery directory", root).returncode, 0)
        tool = root / "tools/build_unified_discovery.py"
        tool.parent.mkdir()
        tool.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "assert sys.argv[1:] == ['--check']\n"
            "assert Path('proposals/discovery/verified.ready').is_file()\n"
            "assert Path('explorer/discovery-catalog.json').read_bytes() == b'source-only\\n'\n",
            encoding="utf-8",
        )
        self.assertNotEqual(self.check_step("Verify optional Multimedia discovery directory", root).returncode, 0)
        (root / "proposals/discovery").mkdir(parents=True)
        (root / "proposals/discovery/verified.ready").touch()
        self.assertEqual(self.check_step("Verify optional Multimedia discovery directory", root).returncode, 0)
        tool.unlink()
        (root / "tools/real_generator.py").write_text("print('ok')\n", encoding="utf-8")
        tool.symlink_to("real_generator.py")
        self.assertNotEqual(self.check_step("Verify optional Multimedia discovery directory", root).returncode, 0)

    def test_extra_file_hidden_directory_and_fifo_are_forbidden(self):
        root = self.fixture()
        extra = root / "explorer/secret.txt"
        extra.write_text("do not publish\n", encoding="utf-8")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        extra.unlink()
        hidden = root / "explorer/.cache"
        hidden.mkdir()
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        hidden.rmdir()
        fifo = root / "explorer/pipe"
        os.mkfifo(fifo)
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)

    def test_hero_artwork_is_required_identical_and_committed(self):
        root = self.fixture()
        public = root / "explorer/trek-data-core-hero.jpg"
        source = root / "docs/assets/trek-data-core-hero.jpg"
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        public.write_bytes(b"altered art")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        public.write_bytes(source.read_bytes())
        self.assertEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        source.write_bytes(b"different original")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        source.write_bytes(public.read_bytes())
        public.unlink()
        public.symlink_to("index.html")
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)

    def test_research_file_or_generator_symlink_refused(self):
        root = self.fixture()
        fifth = root / "explorer/research-leads.json"
        fifth.symlink_to("index.json")
        self.assertNotEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)
        self.assertNotEqual(self.check_step("Verify final public artifact boundary", root).returncode, 0)
        fifth.unlink()
        fifth.write_text("verified\n", encoding="utf-8")
        self.commit_fixture(root)
        tool = root / "tools/build_research_leads.py"
        tool.parent.mkdir()
        (tool.parent / "real_generator.py").write_text("print('ok')\n", encoding="utf-8")
        tool.symlink_to("real_generator.py")
        self.assertNotEqual(self.check_step("Verify optional Research Leads index", root).returncode, 0)


if __name__ == "__main__":
    unittest.main()
