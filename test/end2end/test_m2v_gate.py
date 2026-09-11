"""m2v-multilingual candidate-default gate for ovos-skill-confucius-quotes (en-US).

Boots the skill under the candidate default engine -- the m2v multilingual
classifier (``OpenVoiceOS/ovos-m2v-intents-multi-128M-v5``) via ovoscope's
``get_m2v_minicroft`` -- and replays a representative slice of this skill's
own golden utterances (``golden_utterances.jsonl``) through it. Padatious
stays the skill's deterministic floor (see ``test_golden_utterances.py``);
this gate validates the candidate model that may replace it as the shipping
default.

Each row asserts both routing (the classifier picks this skill's registered
intent id) and effect (the rendered ``speak`` text carries real dialog
content, not the bare dialog name).

Run:
    uv run pytest test/end2end/test_m2v_gate.py -v
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_m2v_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
LANG = "en-US"

GOLDEN_PATH = Path(__file__).parent / "golden_utterances.jsonl"

# One representative utterance per intent, pulled from the skill's own golden set.
ROWS = [
    {"utterance": "quote confucius", "intent_label": "ConfuciusQuote", "dialog": "quote"},
    {"utterance": "when was confucius alive", "intent_label": "ConfuciusLive", "dialog": "live"},
    {"utterance": "when was confucius born", "intent_label": "ConfuciusBirth", "dialog": "birth"},
    {"utterance": "when did confucius die", "intent_label": "ConfuciusDeath", "dialog": "death"},
    {"utterance": "who is confucius", "intent_label": "who", "dialog": "confucius"},
    {"utterance": "tell me a confucius quote", "intent_label": "ConfuciusQuote", "dialog": "quote"},
]


@pytest.fixture(scope="module")
def minicroft():
    mc = get_m2v_minicroft(skill_ids=[SKILL_ID], lang=LANG)
    pipe = mc.intents.pipeline_plugins["ovos-m2v-pipeline"]
    pipe._ensure_model(background_ok=False)
    yield mc
    mc.stop()


def _capture(mc, text, session_id):
    session = Session(session_id)
    session.lang = LANG
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": LANG},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(mc)
    capture.capture(utterance, timeout=30)
    return capture.finish()


@pytest.mark.timeout(60)
@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["utterance"])
def test_m2v_gate(minicroft, row):
    expected_intent = f"{SKILL_ID}:{row['intent_label']}"
    messages = _capture(minicroft, row["utterance"], f"m2v-{row['utterance']}")

    matched = [m for m in messages if m.msg_type == "ovos.intent.matched"]
    assert matched, (
        f"{row['utterance']!r}: expected ovos.intent.matched, got "
        f"{[m.msg_type for m in messages]!r}"
    )
    names = [m.data.get("intent_name") for m in matched]
    assert expected_intent in names, (
        f"{row['utterance']!r}: expected intent_name {expected_intent!r}, got {names!r}"
    )

    speaks = [m for m in messages if m.msg_type in ("speak", "ovos.utterance.speak")]
    assert speaks, f"{row['utterance']!r}: no speak message captured"
    spoken = speaks[0].data.get("utterance", "")
    assert spoken, f"{row['utterance']!r}: empty spoken text"
    # The rendered text must carry real dialog content, not the bare dialog name.
    assert row["dialog"] not in spoken.lower().split() or len(spoken) > len(row["dialog"]) + 5, (
        f"{row['utterance']!r}: spoken text looks like a bare dialog name: {spoken!r}"
    )
    assert spoken.strip().lower() != row["dialog"], (
        f"{row['utterance']!r}: spoken text is literally the dialog name: {spoken!r}"
    )
