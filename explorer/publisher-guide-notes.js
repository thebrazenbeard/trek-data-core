/* Separate, source-local Explorer consumer. Never adds notes to canonical Briefings. */
"use strict";

const byId = (name) => document.getElementById(name);
const search = byId("search");
const series = byId("series");
const withheld = byId("withheld");
const notesArea = byId("notes");
let corpus = [];

function element(name, css, text) {
  const node = document.createElement(name);
  if (css) node.className = css;
  if (text !== undefined) node.textContent = text;
  return node;
}

function detail(list, label, value) {
  const line = element("div");
  const dt = element("dt", "", `${label}: `);
  const dd = element("dd", "", value);
  line.append(dt, dd);
  list.append(line);
}

function card(note) {
  const held = note.review_state === "WITHHELD_MULTIPART_IDENTITY";
  const node = element("article", held ? "note-card withheld" : "note-card");
  const top = element("div", "note-top");
  top.append(element("span", "", `${note.series} / S${note.season} E${note.episode}`),
    element("span", "pill", held ? "WITHHELD" : "HELD · DRAFT"));
  node.append(top, element("h3", "", note.source_local_title));
  node.append(element("p", "summary", note.paraphrase ||
    "No paraphrase: the publisher card combines multipart identity; this ambiguity remains unresolved."));

  const metadata = element("dl", "details");
  detail(metadata, "Evidence frame", "Publisher marketing description, not episode content");
  detail(metadata, "Source locator", note.source_card_locator);
  detail(metadata, "Original packet SHA-256", note.source_packet_sha256);
  detail(metadata, "Card fingerprint", note.publisher_description_sha256 || "Not held / not archived");
  if (note.identity_hold !== "NO_GLOBAL_WORK_IDENTITY_ASSERTED")
    detail(metadata, "Identity caution", note.identity_hold);
  node.append(metadata);

  const actions = element("div", "actions");
  const guide = element("a", "", "Publisher guide ↗");
  guide.href = note.publisher_guide_url;
  guide.target = "_blank";
  guide.rel = "noopener noreferrer";
  const proposal = element("a", "", "Source proposal ↗");
  proposal.href = `https://github.com/thebrazenbeard/trek-data-core/blob/main/${note.source_packet_path}`;
  proposal.target = "_blank";
  proposal.rel = "noopener noreferrer";
  actions.append(guide, proposal);
  node.append(actions);
  return node;
}

function render() {
  const needle = search.value.trim().toLocaleLowerCase();
  const selected = series.value;
  const rows = corpus.filter((note) => {
    if (selected !== "ALL" && note.series !== selected) return false;
    if (withheld.checked && note.review_state !== "WITHHELD_MULTIPART_IDENTITY") return false;
    const haystack = [note.source_local_title, note.paraphrase || "", note.source_local_row_id,
      `${note.series} S${note.season} E${note.episode}`, note.source_card_locator].join(" ").toLocaleLowerCase();
    return haystack.includes(needle);
  });
  notesArea.replaceChildren(...rows.map(card));
  byId("counter").textContent = `${rows.length} matching source-local notes / ${corpus.length} total observations`;
  if (!rows.length) notesArea.append(element("p", "", "No matching held publisher notes. Try another term or series."));
}

async function load() {
  try {
    const response = await fetch("./publisher-guide-notes.json", {cache: "no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    if (result.schema_version !== "trek-held-publisher-guide-notes-v1" ||
        result.data_status !== "HELD_SOURCE_LOCAL_DERIVED_SIDECAR_NOT_CANONICAL" ||
        !Array.isArray(result.notes) || result.notes.length !== result.source_local_observation_count ||
        result.canonical_work_count_added !== 0 || result.canonical_briefing_count_added !== 0 ||
        result.episode_coverage_effect !== "NONE") throw new Error("Source-local sidecar contract mismatch");
    corpus = result.notes;
    [...new Set(corpus.map((note) => note.series))].sort().forEach((name) => {
      const option = element("option", "", name);
      option.value = name;
      series.append(option);
    });
    byId("source-status").textContent =
      `${result.held_paraphrase_count} unapproved paraphrases · ${result.withheld_identity_count} identity hold · 0 canonical Works`;
    render();
  } catch (error) {
    byId("counter").textContent = "Source-local notes unavailable; no canonical index was modified.";
    byId("source-status").textContent = String(error.message || error);
  }
}

[search, series, withheld].forEach((control) => control.addEventListener("input", render));
load();
