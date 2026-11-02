"""Source-only safety checks for the public Pages artifact boundary."""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "static.yml"


def job_body(name):
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [a-z][a-z0-9_-]*:\n|\Z)",
        text.split("\njobs:\n", 1)[1],
    )
    if match is None:
        raise AssertionError(f"missing job: {name}")
    return match.group(1)


class PagesArtifactScopeTests(unittest.TestCase):
    def run_step(self, step_name, workspace):
        """Execute the workflow's actual bash body in a temporary fixture."""
        rows = WORKFLOW.read_text(encoding="utf-8").splitlines()
        header = f"      - name: {step_name}"
        self.assertIn(header, rows)
        start = rows.index(header)
        run_line = next(
            i for i in range(start + 1, len(rows))
            if rows[i] == "        run: |"
        )
        script = []
        for line in rows[run_line + 1:]:
            if line.startswith("      - name:"):
                break
            if line.strip():
                self.assertTrue(line.startswith("          "), line)
                script.append(line[10:])
            else:
                script.append("")
        self.assertTrue(script)
        return subprocess.run(
            ["bash", "-e", "-u", "-o", "pipefail", "-c", "\n".join(script)],
            cwd=workspace, capture_output=True, text=True, check=False,
        )

    def temporary_explorer(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        workspace = Path(temp.name)
        explorer = workspace / "explorer"
        explorer.mkdir()
        for name in ("index.html", "index.json", "app.js", "app.css"):
            (explorer / name).write_text("verified\n", encoding="utf-8")
        self.commit_fixture(workspace)
        return workspace

    def commit_fixture(self, workspace):
        if not (workspace / ".git").exists():
            first = subprocess.run(["git", "init", "-q"], cwd=workspace, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
        for cmd in (
            ["git", "add", "--", "explorer"],
            ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "commit", "-qm", "Accepted Explorer fixture"],
        ):
            result = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_artifact_is_only_the_explorer_directory(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: explorer", text)
        self.assertNotIn("path: '.'", text)
        self.assertNotIn('path: "."', text)

    def test_requires_index_and_entrypoint(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test -f explorer/index.html", text)
        self.assertIn("test -f explorer/index.json", text)

    def test_drops_unfinished_template_steps(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("actions/cache@", text)
        self.assertNotIn("actions/setup-dotnet@", text)
        self.assertIn("actions/upload-pages-artifact@v4", text)

    def test_catalog_changes_redeploy_only_after_exact_regeneration(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"registry/mission_catalog.json"', text)
        self.assertIn('"tools/build_explorer_index.py"', text)
        self.assertIn('"registry/approved_projection_hashes.json"', text)
        self.assertIn("python3 tools/build_explorer_index.py", text)
        self.assertIn('cmp "${RUNNER_TEMP}/trek-index-expected.json" explorer/index.json', text)

    def test_deployment_gates_on_behavior_and_exact_allowlist(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", text)
        self.assertIn("node tests/test_explorer.mjs", text)
        self.assertIn("python3 -m unittest discover", text)
        self.assertIn("! -path explorer/app.js", text)
        self.assertIn("! -path explorer/app.css", text)
        self.assertIn("! -path explorer/research-leads.json", text)
        self.assertIn("Refusing to publish an unexpected Explorer file", text)

    def test_manual_dispatch_cannot_deploy_a_review_branch(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: github.ref == 'refs/heads/main'", text)
        self.assertIn("if: needs.build.outputs.ready == 'true' && github.ref == 'refs/heads/main'", text)

    def test_pages_can_land_first_without_publishing_missing_explorer(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("id: readiness", text)
        self.assertIn("ready=false", text)
        self.assertIn("skipping Pages publication", text)
        self.assertEqual(text.count("if: steps.readiness.outputs.ready == 'true'"), 5)
        self.assertIn("ready: ${{ steps.readiness.outputs.ready }}", job_body("build"))
        self.assertIn("needs: build", job_body("deploy"))

    def test_repo_code_has_no_pages_or_oidc_privilege(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("permissions:", source.split("\njobs:\n", 1)[0])
        build = job_body("build")
        self.assertRegex(build, r"(?m)^    permissions:\n      contents: read$")
        self.assertNotIn("pages: write", build)
        self.assertNotIn("id-token: write", build)
        self.assertIn("actions/checkout@", build)
        self.assertIn("persist-credentials: false", build)
        self.assertIn("python3 tools/build_research_leads.py --check", build)
        self.assertIn("node tests/test_explorer.mjs", build)
        self.assertIn("actions/upload-pages-artifact@v4", build)
        self.assertNotIn("actions/deploy-pages@", build)

    def test_deploy_job_is_action_only_and_gated(self):
        deploy = job_body("deploy")
        self.assertRegex(deploy, r"(?m)^    permissions:\n      pages: write\n      id-token: write$")
        self.assertIn("needs: build", deploy)
        self.assertIn("if: needs.build.outputs.ready == 'true'", deploy)
        self.assertIn("uses: actions/deploy-pages@v5", deploy)
        self.assertNotIn("actions/checkout@", deploy)
        self.assertNotIn("actions/configure-pages@", deploy)
        self.assertNotIn("run:", deploy)
        self.assertEqual(deploy.count("uses:"), 1)

    def test_research_leads_change_triggers_guarded_republication(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"tools/build_research_leads.py"', text)
        self.assertIn('"proposals/discovery/wikidata-tng-q16290-20261102/**"', text)
        self.assertIn('"proposals/discovery/wikidata-mission-samples-20261102/**"', text)
        self.assertIn("python3 tools/build_research_leads.py --check", text)
        self.assertLess(text.index("Verify Explorer behavior before deployment"),
                        text.index("Verify deterministic catalog index"))
        self.assertLess(text.index("Verify deterministic catalog index"),
                        text.index("Verify optional Research Leads index"))
        self.assertLess(text.index("Verify optional Research Leads index"),
                        text.index("Verify final public artifact boundary"))
        self.assertLess(text.index("Verify final public artifact boundary"),
                        text.index("Upload Explorer only"))
        self.assertIn('git rev-parse "HEAD:$path"', text)
        self.assertIn('git hash-object "$path"', text)

    def test_optional_fifth_file_absent_keeps_four_file_release_safe(self):
        workspace = self.temporary_explorer()
        self.assertEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)
        self.assertEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)
        self.assertFalse((workspace / "tools/build_research_leads.py").exists())

    def test_optional_file_without_generator_fails_closed(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(workspace)
        self.assertEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)
        self.assertNotEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)

    def test_optional_public_file_must_be_committed(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").write_text("unreviewed\n", encoding="utf-8")
        self.assertNotEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)

    def test_post_test_mutation_of_required_asset_is_blocked(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/app.js").write_text("modified after tests\n", encoding="utf-8")
        self.assertNotEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)

    def test_present_optional_file_requires_checkable_source_provenance(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(workspace)
        tools_dir = workspace / "tools"
        tools_dir.mkdir()
        # Synthetic command stand-in: assert the workflow invokes --check and
        # propagates a verifier failure. Real generator tests live separately.
        (tools_dir / "build_research_leads.py").write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "assert sys.argv[1:] == ['--check']\n"
            "assert Path('proposals/discovery/candidates.ready').is_file()\n"
            "assert Path('explorer/research-leads.json').read_bytes() == b'verified\\n'\n",
            encoding="utf-8",
        )
        self.assertNotEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)
        (workspace / "proposals/discovery").mkdir(parents=True)
        (workspace / "proposals/discovery/candidates.ready").touch()
        self.assertEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)
        self.assertEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)
        (workspace / "explorer/research-leads.json").write_text("tampered\n", encoding="utf-8")
        self.assertNotEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)
        self.assertNotEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)

    def test_unexpected_sixth_file_still_refused(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(workspace)
        (workspace / "explorer/secret.txt").write_text("not public\n", encoding="utf-8")
        self.assertNotEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)

    def test_optional_symlink_source_or_public_file_refused(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").symlink_to("index.json")
        self.assertNotEqual(self.run_step("Verify final public artifact boundary", workspace).returncode, 0)

    def test_optional_generator_symlink_refused_even_with_valid_public_bytes(self):
        workspace = self.temporary_explorer()
        (workspace / "explorer/research-leads.json").write_text("verified\n", encoding="utf-8")
        self.commit_fixture(workspace)
        tools_dir = workspace / "tools"
        tools_dir.mkdir()
        (tools_dir / "real_generator.py").write_text("print('ok')\n", encoding="utf-8")
        (tools_dir / "build_research_leads.py").symlink_to("real_generator.py")
        self.assertNotEqual(self.run_step("Verify optional Research Leads index", workspace).returncode, 0)


if __name__ == "__main__":
    unittest.main()
