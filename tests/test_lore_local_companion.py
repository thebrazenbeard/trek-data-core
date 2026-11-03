"""Adversarial no-network tests of opt-in localhost Lore companion boundaries."""

import contextlib
import http.client
import json
import socket
import threading
import unittest
from unittest import mock

from tools import lore_local_companion as lore


TOKEN = "A" * 40


def sample_source(text):
    return {
        "status": "SOURCE_LOCAL_HELD_ONLY",
        "identity_scope": "SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK",
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "matching_count": 1,
        "returned_count": 1,
        "rows": [{
            "source_local_id": "snw-s3-e02-pplus",
            "title": "Wedding Bell Blues",
            "series_code": "SNW",
            "source_status": "HELD_PUBLISHER_GUIDE_ONLY",
            "source_batch": "SNW-FIRST5",
            "source_row_sha256": "a" * 64,
            "publisher_family": "publisher:paramountplus.com",
            "publisher_utterance_labels": ["Spock"],
        }],
    }


@contextlib.contextmanager
def local_server(*, model_url=None, search=sample_source, model=None):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    service = lore.LoreService(port=port, token=TOKEN, model_url=model_url,
                              search=search,
                              model=model if model is not None else lore.local_model_answer)
    server = lore.create_server(service)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def request(port, *, method="POST", path="/api/query", query="Spock", headers=None,
            raw=None):
    body = json.dumps({"query": query}).encode() if raw is None else raw
    request_headers = {
        "Host": f"127.0.0.1:{port}",
        "Origin": f"http://127.0.0.1:{port}",
        "X-Trek-Lore-CSRF": TOKEN,
        "Content-Type": "application/json",
    }
    if headers:
        request_headers.update(headers)
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        conn.request(method, path, body=body, headers=request_headers)
        response = conn.getresponse()
        output = response.read()
        return response.status, response.getheaders(), json.loads(output)
    finally:
        conn.close()


class LoreCompanionTests(unittest.TestCase):
    def test_disabled_by_default_never_creates_listener(self):
        with mock.patch.object(lore, "create_server", side_effect=AssertionError("listen")):
            self.assertEqual(lore.main([]), 2)

    def test_model_url_requires_exact_numeric_loopback_path_and_no_redirect(self):
        okay = "http://127.0.0.1:9931/v1/chat/completions"
        self.assertEqual(lore.verify_model_url(okay), okay)
        for invalid in (
            "https://127.0.0.1:9931/v1/chat/completions",
            "http://localhost:9931/v1/chat/completions",
            "http://0.0.0.0:9931/v1/chat/completions",
            "http://example.com:9931/v1/chat/completions",
            "http://127.0.0.1:9931/api/v1/generate",
            "http://127.0.0.1:9931/v1/chat/completions#fragment",
            "http://user:pass@127.0.0.1:9931/v1/chat/completions",
            "http://127.0.0.1:bad/v1/chat/completions",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                lore.verify_model_url(invalid)
        self.assertIsNone(lore._NoRedirect().redirect_request(None, None, 302, "", {}, "http://evil"))

    def test_token_and_listener_validation(self):
        with self.assertRaises(ValueError):
            lore.LoreService(port=9876, token="x")
        with self.assertRaises(ValueError):
            lore.LoreService(port=0, token=TOKEN)
        with self.assertRaises(ValueError):
            lore.LoreService(port=9876, token=TOKEN,
                             model_url="http://127.0.0.1:9876/v1/chat/completions")

    def test_actual_trusted_search_uses_pinned_held_shelf_only(self):
        result = lore.trusted_source_search("Spock")
        self.assertEqual(result["status"], "SOURCE_LOCAL_HELD_ONLY")
        self.assertEqual(result["identity_scope"], "SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK")
        self.assertEqual(result["matching_count"], 1)
        self.assertTrue(all(row["source_row_sha256"] for row in result["rows"]))
        self.assertEqual(result["admission_effect"], "NONE")
        self.assertEqual(result["coverage_effect"], "NONE")

    def test_model_is_disabled_by_default_and_status_is_not_from_model(self):
        with local_server(model=lambda *_: self.fail("unexpected model call")) as port:
            status, headers, output = request(port)
            self.assertEqual(status, 200)
            self.assertEqual(output["mode"], "verified_source_search_only")
            self.assertIsNone(output["model_text"])
            self.assertEqual(output["source_search"]["status"], "SOURCE_LOCAL_HELD_ONLY")
            self.assertEqual(output["publication_effect"], "NONE")
            self.assertEqual(output["model_repo_authority"], "NONE")
            self.assertNotIn("Access-Control-Allow-Origin", dict(headers))
            self.assertEqual(dict(headers)["Cache-Control"], "no-store")

    def test_unsafe_origins_tokens_host_and_cors_fail_closed(self):
        with local_server() as port:
            for headers in (
                {"Origin": "https://thebrazenbeard.github.io"},
                {"Origin": ""},
                {"X-Trek-Lore-CSRF": "bad"},
                {"Host": "attacker.example"},
                {"Host": "localhost:%d" % port},
            ):
                with self.subTest(headers=headers):
                    status, values, _ = request(port, headers=headers)
                    self.assertEqual(status, 403)
                    self.assertNotIn("Access-Control-Allow-Origin", dict(values))
            for method in ("GET", "OPTIONS"):
                status, values, _ = request(port, method=method)
                self.assertEqual(status, 405)
                self.assertNotIn("Access-Control-Allow-Origin", dict(values))

    def test_bounded_schema_media_and_route(self):
        with local_server() as port:
            invalid = (
                ("/unknown", None, None, 404),
                ("/api/query", {"Content-Type": "text/plain"}, None, 415),
                ("/api/query", None, b"{" + b"x" * 2100 + b"}", 413),
                ("/api/query", None, b'{"query":"Spock","admin":true}', 400),
                ("/api/query", None, b'{"query":"Spock","query":"Lore"}', 400),
                ("/api/query", None, b'{"query":"\\u0000"}', 400),
                ("/api/query", None, b'{"query":2}', 400),
            )
            for path, headers, raw, expected in invalid:
                with self.subTest(path=path, raw=raw):
                    status, _, _ = request(port, path=path, headers=headers, raw=raw)
                    self.assertEqual(status, expected)
            # An all-digit, attacker-sized length used to reach int() before
            # the error handler, closing the socket rather than returning JSON.
            status, _, output = request(port, headers={"Content-Length": "9" * 10000})
            self.assertEqual(status, 400)
            self.assertEqual(output["error"], "invalid request length")

    def test_source_validator_failure_cannot_be_turned_into_answer(self):
        def fail(_):
            raise ValueError("source sha mutated")
        with local_server(search=fail) as port:
            status, _, output = request(port)
            self.assertEqual(status, 400)
            self.assertNotIn("source sha", output["error"])

    def test_source_status_spoofing_rejected_before_model(self):
        fake = sample_source("X")
        fake["admission_effect"] = "ADMITTED_WORK"
        with local_server(search=lambda _: fake,
                          model=lambda *_: self.fail("model must not see spoofed source")) as port:
            status, _, _ = request(port)
            self.assertEqual(status, 400)

    def test_model_failure_is_safe_503_without_echoing_model_error(self):
        def failing_model(*_):
            raise ValueError("forged model internals and token")
        with local_server(model_url="http://127.0.0.1:9931/v1/chat/completions",
                          model=failing_model) as port:
            status, _, output = request(port)
            self.assertEqual(status, 503)
            self.assertNotIn("forged", str(output))

    def test_opted_in_model_text_never_mutates_trusted_source_or_authority(self):
        hostile_reply = '"citation": "verified canon"; "admission_effect": "ADMITTED"'
        with local_server(model_url="http://127.0.0.1:9931/v1/chat/completions",
                          model=lambda *_: hostile_reply) as port:
            status, _, output = request(port)
            self.assertEqual(status, 200)
            self.assertEqual(output["mode"], "opt_in_unverified_model_prose")
            self.assertTrue(output["model_text_unverified"])
            self.assertEqual(output["model_text"], hostile_reply)
            self.assertEqual(output["source_search"]["admission_effect"], "NONE")
            self.assertEqual(output["model_repo_authority"], "NONE")

    def test_no_model_network_call_when_source_has_no_matches(self):
        empty = sample_source("X")
        empty["rows"] = []
        empty["matching_count"] = 0
        empty["returned_count"] = 0
        with local_server(model_url="http://127.0.0.1:9931/v1/chat/completions",
                          search=lambda _: empty,
                          model=lambda *_: self.fail("model must not invent for absent sources")) as port:
            status, _, output = request(port)
            self.assertEqual(status, 200)
            self.assertEqual(output["source_search"]["matching_count"], 0)
            self.assertEqual(output["mode"], "verified_source_search_only")


if __name__ == "__main__":
    unittest.main()
