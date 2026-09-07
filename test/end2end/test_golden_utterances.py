"""Golden-utterance end-to-end coverage for ovos-skill-confucius-quotes (en-US).

``golden_utterances.jsonl`` vendors the shared ovoscope corpus slice for
``ovos-skill-confucius-quotes.openvoiceos`` supplemented with rows derived
from this skill's own dialogs/vocab and its existing smoke test, for broader
phrasing coverage. Both ``Confucius*`` intents are matched via Padatious
``.intent`` templates rather than Adapt. Padatious templates are order
sensitive, so the original corpus rows that relied on Adapt's
order-independent ``.require()`` matching ("alive when confucius", "birth
confucius", "death confucius") were reworded to a canonical phrasing that the
``.intent`` templates actually cover; "quote confucius" is covered literally
and was kept unchanged.

Each row is asserted via the ``ovos.intent.matched`` bus message's
``data.intent_name`` field (observed directly against this skill's message
stream, confirming it is emitted here -- unlike some other skills in this
wave where only the bare ``<skill_id>:<Intent>`` msg_type appears).

Run:
    uv run pytest test/end2end/ -v
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
LANG = "en-US"

_PIPELINE = [
    "ovos-adapt-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-padacioso-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-low",
]

GOLDEN_PATH = Path(__file__).parent / "golden_utterances.jsonl"

# Confusables lifted from other skills' domains: biography/"who is" skills
# (wikipedia), other quote/quiz skills, and generic knowledge-query skills
# that could plausibly claim "who is X" / "when did X" phrasing.
NEGATIVE_UTTERANCES = [
    ("who is albert einstein", "ovos-skill-wikipedia.openvoiceos"),
    ("what's the weather", "ovos-skill-weather.openvoiceos"),
    ("tell me a joke", "skill-icanhazdadjokes.openvoiceos"),
    ("search the web for philosophy", "ovos-skill-ddg.openvoiceos"),
    ("play some music", "ovos-skill-music.openvoiceos"),
    ("when is my next alarm", "ovos-skill-alerts.openvoiceos"),
    ("who is the president of the united states", "ovos-skill-wolfie.openvoiceos"),
]


def _load_golden_rows():
    rows = []
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("needs_manual"):
                continue
            rows.append(row)
    return rows


GOLDEN_ROWS = [pytest.param(r, id=r["utterance"]) for r in _load_golden_rows()]


@pytest.fixture(scope="module")
def minicroft():
    mc = get_minicroft([SKILL_ID])
    yield mc
    mc.stop()


def _capture(mc, text, session_id):
    session = Session(session_id)
    session.lang = LANG
    session.pipeline = list(_PIPELINE)
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": LANG},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(mc)
    capture.capture(utterance, timeout=30)
    return capture.finish()


@pytest.mark.timeout(60)
@pytest.mark.parametrize("row", GOLDEN_ROWS, ids=lambda r: r["utterance"])
def test_golden_utterance(minicroft, row):
    expected_intent = f"{SKILL_ID}:{row['intent_label']}"
    messages = _capture(minicroft, row["utterance"], f"golden-{row['utterance']}")
    matched = [m for m in messages if m.msg_type == "ovos.intent.matched"]
    assert matched, (
        f"{row['utterance']!r}: expected ovos.intent.matched, got "
        f"{[m.msg_type for m in messages]!r}"
    )
    names = [m.data.get("intent_name") for m in matched]
    assert expected_intent in names, (
        f"{row['utterance']!r}: expected intent_name {expected_intent!r}, got {names!r}"
    )


@pytest.mark.timeout(60)
@pytest.mark.parametrize("negative", NEGATIVE_UTTERANCES, ids=lambda n: n[0])
def test_negative_confusable_not_claimed(minicroft, negative):
    text, source_skill = negative
    messages = _capture(minicroft, text, f"negative-{text}")
    matched = [m for m in messages if m.msg_type == "ovos.intent.matched"]
    claimed = any(
        (m.data.get("intent_name") or "").startswith(f"{SKILL_ID}:") for m in matched
    )
    assert not claimed, f"{text!r} (from {source_skill}) was incorrectly claimed by {SKILL_ID}"
