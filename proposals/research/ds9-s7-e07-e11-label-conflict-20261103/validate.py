"""Strict, nonadmitting five-card DS9 S7E7–E11 publisher source-label gate."""

import csv
import hashlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSV_PATH = ROOT / "proposals/discovery/publisher-season7-20261102/ds9.csv"
INDEX_PATH = ROOT / "proposals/discovery/publisher-season7-20261102/index.json"
DIRECTORY_PATH = ROOT / "explorer/discovery-catalog.json"
BASE = "1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b"
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/"
CSV_SHA = "1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
OLD_PAGE_SHA = "23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1"
OBS_SHA = "d899f96cf1308fc86fed4a8eb9fa5ee64543ab163f872eb88820e9f5ba029046"
CLAIM_SHA = "1d38e07ab4901a773aa0971f99156630e4d370d14c13061eeef041f084083b52"
TITLES = (
    "Once More Unto the Breach", "The Siege of AR-555", "Covenant",
    "It's Only A Paper Moon", "Prodigal Daughter",
)
CONFLICT_REFS = (
    ("https://www.startrek.com/videos/episode-preview-the-siege-of-ar-558",
     "Episode Preview: The Siege of AR-558", "2014-11-05",
     "FIRST_PARTY_VIDEO_PREVIEW_PAGE_TITLE_NOT_EPISODE_VIEWING"),
    ("https://www.startrek.com/en-un/news/fan-favorite-deep-space-nine-quotes",
     "The Siege of AR-558, Season 7, Episode 8", "2023-01-03",
     "FIRST_PARTY_EDITORIAL_ARTICLE_TITLE_REFERENCE_NOT_EPISODE_VIEWING"),
)
ROOT_KEYS = {"schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
             "observed_utc_date", "publisher_guide_url", "primary_publisher_family",
             "comparison_csv_sha256", "historical_publisher_page_sha256",
             "current_publisher_page_raw_sha256", "current_source_read_level",
             "actual_episode_or_script_content_read", "accepted_source_work_effect",
             "coverage_effect", "public_synopsis_effect", "records"}
RECORD_KEYS = {"evidence_id", "source_local_row_id", "season", "episode",
               "historical_and_current_paramount_title", "publisher_card_locator",
               "title_resolution", "same_family_conflict_sources",
               "original_card_description_paraphrase", "editorial_status", "accepted_work_id"}
CONFLICT_KEYS = {"uri", "observed_label", "page_date", "observation_scope"}
CLAIM_KEYS = {"schema_version", "batch_id", "accepted_assertions", "projection_effect", "assertions"}
CLAIM_ROW_KEYS = {"id", "predicate", "subject_source_local_row_id",
                  "supporting_evidence_ids", "status", "claim", "counter_evidence_locator", "falsifier"}


def require(value, message):
    if not value:
        raise ValueError(message)


def closed(obj, expected, scope):
    require(type(obj) is dict and set(obj) == set(expected), f"{scope}: unknown or missing fields")


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def unique_keys(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, f"duplicate key: {k}")
        result[k] = v
    return result


def read(path):
    require(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size < 4_000_000,
            "source input unreadable, symlinked, empty or oversized")
    return path.read_bytes()


def read_json(path):
    return json.loads(read(path).decode("utf-8"), object_pairs_hook=unique_keys)


def check(obs, claims, directory, directory_raw, csv_raw, old_index):
    closed(obs, ROOT_KEYS, "observations")
    require(obs["schema_version"] == "1.0.0"
            and obs["batch_id"] == "ds9-s7-e07-e11-label-conflict-20261103"
            and obs["role"] == "DS9" and obs["proposal_only"] is True
            and obs["accepted_main_at_selection"] == BASE
            and obs["observed_utc_date"] == "2026-11-03", "scope and date changed")
    require(obs["publisher_guide_url"] == URL
            and obs["primary_publisher_family"] == "paramount_corporate_publisher_family"
            and obs["current_source_read_level"] == "RENDERED_EPISODE_GUIDE_TITLE_SLOT_BLURB_ONLY",
            "publisher source or fidelity changed")
    require(obs["comparison_csv_sha256"] == CSV_SHA
            and hashlib.sha256(csv_raw).hexdigest() == CSV_SHA
            and obs["historical_publisher_page_sha256"] == OLD_PAGE_SHA,
            "old publisher source receipt changed")
    require(obs["current_publisher_page_raw_sha256"] is None
            and obs["actual_episode_or_script_content_read"] is False,
            "unsupported current source body or episode-read claim")
    for field in ("accepted_source_work_effect", "coverage_effect", "public_synopsis_effect"):
        require(obs[field] == "NONE", f"unexpected {field}")

    require(type(old_index) is dict and old_index.get("proposal_status") == "DISCOVERY_ONLY"
            and old_index.get("admission_effect") == "NONE"
            and old_index.get("coverage_effect") == "NONE"
            and old_index.get("denominator_effect") == "NONE"
            and old_index.get("independence_group") == "publisher:paramount"
            and old_index.get("observed_on") == "2026-11-02", "historical source family drift")
    old_ds9 = [page for page in old_index.get("source_pages", [])
               if page.get("mission_id") == "ds9"]
    require(len(old_ds9) == 1 and old_ds9[0].get("official_page") == URL
            and old_ds9[0].get("observation_csv_sha256") == CSV_SHA
            and old_ds9[0].get("source_body_sha256") == OLD_PAGE_SHA
            and old_ds9[0].get("source_body_bytes") == 314706,
            "old DS9 page custody receipt not matched")

    require(type(directory) is dict and directory.get("data_status") == "DISCOVERY_ONLY"
            and directory.get("admission_effect") == "NONE"
            and directory.get("coverage_effect") == "NONE"
            and directory.get("row_count") == 1214
            and len(directory.get("rows", [])) == 1214
            and hashlib.sha256(directory_raw).hexdigest() == DIRECTORY_SHA,
            "source-local directory or coverage drift")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == 1214, "directory ID collision")
    parsed = list(csv.DictReader(io.StringIO(csv_raw.decode("utf-8"))))
    require(len(parsed) == 25 and type(obs["records"]) is list
            and len(obs["records"]) == 5, "publisher season or batch scope drift")

    for n, row in enumerate(obs["records"]):
        closed(row, RECORD_KEYS, "publisher episode card")
        season, episode, title = 7, n + 7, TITLES[n]
        expected_id = f"publisher:s7:ds9:{episode - 1:03d}"
        source = by_id[expected_id]
        require(parsed[episode - 1] == {"season": "7", "episode_number": str(episode),
                                        "title": title}, "historical CSV title/slot changed")
        require(source.get("title") == title and source.get("context") == f"DS9 S7E{episode}"
                and source.get("medium") == "EPISODE"
                and source.get("source_group") == "publisher:paramount"
                and source.get("source_locator") == URL
                and source.get("verification_status") == "UNVERIFIED_METADATA"
                and source.get("admission_effect") == "NONE"
                and source.get("coverage_effect") == "NONE", "unreviewed directory row promoted")
        require(row["evidence_id"] == f"ds9-s7e07-11-p{n + 1:02d}"
                and row["source_local_row_id"] == expected_id
                and type(row["season"]) is int and row["season"] == season
                and type(row["episode"]) is int and row["episode"] == episode
                and row["historical_and_current_paramount_title"] == title,
                "current official card identity or order changed")
        require(row["publisher_card_locator"] == (
            f"Season 7 Episode Guide > {title} > S7 E{episode} > short description"
        ) and row["accepted_work_id"] is None, "source card locator or Work effect altered")
        if episode == 8:
            require(row["title_resolution"] == "NUMERIC_TITLE_CONFLICT_WITH_SAME_FAMILY_STAR_TREK_SITE_UNRESOLVED"
                    and row["original_card_description_paraphrase"] is None
                    and row["editorial_status"] == "WITHHELD_UNRESOLVED_SAME_FAMILY_NUMERIC_TITLE_CONFLICT",
                    "numeric publisher label dispute falsely resolved")
            variants = row["same_family_conflict_sources"]
            require(type(variants) is list and len(variants) == 2,
                    "insufficient conflict source locators")
            for variant, (uri, label, date, scope) in zip(variants, CONFLICT_REFS):
                closed(variant, CONFLICT_KEYS, "first-party label variant")
                require(variant == {"uri": uri, "observed_label": label,
                                    "page_date": date, "observation_scope": scope},
                        "first-party source label or locator changed")
        else:
            require(row["title_resolution"] == "EXACT_WITH_HISTORICAL_PUBLISHER_CSV"
                    and row["same_family_conflict_sources"] == []
                    and row["editorial_status"] == "PENDING_HUMAN_REVIEW",
                    "invented source disagreement or synopsis approval")
            draft = row["original_card_description_paraphrase"]
            require(type(draft) is str and 65 <= len(draft) <= 220
                    and draft.endswith(".") and "\n" not in draft,
                    "unreviewed blurb draft invalid")

    closed(claims, CLAIM_KEYS, "assertions envelope")
    require(claims["schema_version"] == "1.0.0"
            and claims["batch_id"] == obs["batch_id"]
            and claims["accepted_assertions"] == 0
            and claims["projection_effect"] == "NONE"
            and type(claims["assertions"]) is list
            and len(claims["assertions"]) == 1, "claim lifecycle promoted")
    claim = claims["assertions"][0]
    closed(claim, CLAIM_ROW_KEYS, "unresolved claim")
    require(claim["id"] == "ds9-s7e07-11-a01"
            and claim["predicate"] == "PUBLISHER_FAMILY_TITLE_LABEL_DISAGREEMENT_UNRESOLVED"
            and claim["subject_source_local_row_id"] == "publisher:s7:ds9:007"
            and claim["supporting_evidence_ids"] == ["ds9-s7e07-11-p02"]
            and claim["status"] == "PROPOSED_UNRESOLVED"
            and claim["counter_evidence_locator"] == CONFLICT_REFS[1][0]
            and type(claim["falsifier"]) is str and len(claim["falsifier"]) > 70,
            "unresolved title label claim altered")
    require(digest(obs) == OBS_SHA and digest(claims) == CLAIM_SHA,
            "source-local candidate observation/claim changed without review")


def validate():
    obs = read_json(HERE / "observations.json")
    claims = read_json(HERE / "assertions.json")
    directory_raw = read(DIRECTORY_PATH)
    directory = json.loads(directory_raw.decode("utf-8"), object_pairs_hook=unique_keys)
    check(obs, claims, directory, directory_raw, read(CSV_PATH), read_json(INDEX_PATH))
    print("DS9_S7_E07_E11_OK: five publisher card titles/slots; one AR-555 vs AR-558 same-family "
          "conflict held, four unpublished draft paraphrases; no Work/coverage effects")


if __name__ == "__main__":
    validate()
