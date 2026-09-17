"""Multilingual golden-utterance end-to-end coverage for
ovos-skill-confucius-quotes.

test_golden_utterances.py only exercises en-US; every locale under
locale/ ships all three .intent files (confucius_quote,
confucius_lifespan, who), so this suite covers every locale in the fleet.

Both intents are matched via Padatious-family .intent templates (order
sensitive). Each row here is a mechanical expansion of that locale's own
template lines (its own bracket-alternation choices), never a translation
of the English rows.

Assertion follows test_golden_utterances.py: the ovos.intent.matched bus
message's data.intent_name field.

One MiniCroft is booted PER LOCALE (module-scoped fixture, indirectly
parametrized by lang; pytest reuses one boot per distinct lang value
across every row of that lang and tears it down before moving on).
Padatious itself is kept out of the boot (default_pipeline restricted to
padacioso) -- padatious's fann/numpy training runs in an uncancellable
background thread that can hang the whole suite on a contended box.
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"

_PIPELINE = [
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-medium",
]

END2END_DIR = Path(__file__).parent

LANGS = [
    "en-US", "ca-ES", "da-DK", "de-DE", "es-ES", "eu-ES", "fr-FR",
    "gl-ES", "it-IT", "kab", "nl-NL", "pt-BR", "pt-PT", "sv-SE",
]


def _load_rows(lang):
    path = END2END_DIR / f"golden_utterances_{lang}.jsonl"
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("needs_manual"):
                continue
            rows.append(row)
    return rows


ALL_ROWS = []
for _lang in LANGS:
    for _row in _load_rows(_lang):
        ALL_ROWS.append(_row)


def _golden_id(row):
    return f"{row['lang']}-{row['intent_label']}-{row['utterance']}"


@pytest.fixture(scope="module")
def minicroft(request):
    lang = request.param
    mc = get_minicroft(
        [SKILL_ID], max_wait=150, lang=lang,
        default_pipeline=_PIPELINE,
    )
    yield mc
    mc.stop()


def _capture(mc, text, lang, session_id):
    session = Session(session_id)
    session.lang = lang
    session.pipeline = list(_PIPELINE)
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": lang},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(mc)
    capture.capture(utterance, timeout=30)
    return capture.finish()


KNOWN_BUGS = {}

_PARAMS = [
    pytest.param(row["lang"], row, id=_golden_id(row))
    for row in ALL_ROWS
]


@pytest.mark.timeout(300)
@pytest.mark.parametrize("minicroft,row", _PARAMS, indirect=["minicroft"])
def test_golden_utterance_multilang(minicroft, row):
    expected_intent = f"{SKILL_ID}:{row['intent_label']}"
    messages = _capture(minicroft, row["utterance"], row["lang"], f"golden-{_golden_id(row)}")
    matched_msgs = [m for m in messages if m.msg_type == "ovos.intent.matched"]
    names = [m.data.get("intent_name") for m in matched_msgs]
    matched = expected_intent in names
    bug_key = (row["lang"], row["utterance"])
    if bug_key in KNOWN_BUGS and not matched:
        pytest.xfail(reason=f"known-bug: {KNOWN_BUGS[bug_key]}")
    assert matched, (
        f"[{row['lang']}] {row['utterance']!r}: expected intent_name {expected_intent!r}, got {names!r} "
        f"(types={[m.msg_type for m in messages]!r})"
    )
