"""Source-only safety checks for the public Pages artifact boundary."""

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
        self.assertEqual(text.count("if: steps.readiness.outputs.ready == 'true'"), 4)
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
        self.assertIn("actions/upload-pages-artifact@v4", build)
        self.assertNotIn("actions/deploy-pages@", build)

    def test_privileged_deploy_job_runs_no_repo_code(self):
        deploy = job_body("deploy")
        self.assertRegex(deploy, r"(?m)^    permissions:\n      pages: write\n      id-token: write$")
        self.assertIn("needs: build", deploy)
        self.assertIn("if: needs.build.outputs.ready == 'true'", deploy)
        self.assertIn("uses: actions/deploy-pages@v5", deploy)
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
                        text.index("Verify final public artifact boundary"))
        self.assertLess(text.index("Verify final public artifact boundary"),
                        text.index("Upload Explorer only"))
        self.assertIn('cmp "${RUNNER_TEMP}/trek-index-expected.json" explorer/index.json', text)
        final = workflow_step("Verify final public artifact boundary")
        self.assertIn('git rev-parse "HEAD:$path"', final)
        self.assertIn('git hash-object "$path"', final)
        self.assertIn("Refusing to publish an unexpected Explorer file", final)

    def test_final_barrier_rejects_post_test_modifications_and_new_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            explorer = root / "explorer"
            explorer.mkdir()
            for name in ("index.html", "index.json", "app.js", "app.css"):
                (explorer / name).write_text("accepted bytes\n", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
