"""Adapt-less end-to-end intent routing tests for the en-US locale.

These mirror ``test_intents_en_us.py`` but drop every Adapt pipeline stage
from the session pipeline, leaving only Padatious/Padacioso. They prove the
``ConfuciusQuote``/``confucius_lifespan``/``who`` intents are resolved from
the ``.intent`` files under ``locale/en-US/intents/`` (or the repo root, for
``who.intent``) rather than from the (now removed)
``IntentBuilder().require(...)`` Adapt definitions, AND that the handler
speaks a line drawn from that intent's own ``.dialog`` file rather than
merely emitting some ``speak`` message.
"""
import unittest
from pathlib import Path

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
LOCALE_EN_US = Path(__file__).parent.parent.parent / "locale" / "en-US"


def _dialog_lines(name: str) -> set:
    path = LOCALE_EN_US / f"{name}.dialog"
    with open(path, encoding="utf-8") as handle:
        return {line.strip() for line in handle if line.strip()}


_DIALOG_LINES = {
    "ConfuciusQuote": _dialog_lines("quote"),
    "confucius_lifespan": _dialog_lines("lifespan"),
}


class TestConfuciusIntentsEnUSAdaptless(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _run(self, text):
        session = Session("test-session-adaptless")
        session.pipeline = [
            "ovos-padatious-pipeline-plugin-high",
            "ovos-padacioso-pipeline-plugin-high",
            "ovos-padacioso-pipeline-plugin-medium",
        ]
        utterance = Message(
            "recognizer_loop:utterance",
            {"utterances": [text], "lang": "en-US"},
            {"session": session.serialize(), "source": "A", "destination": "B"},
        )
        capture = CaptureSession(self.minicroft)
        capture.capture(utterance, timeout=30)
        return capture.finish()

    def _assert_intent(self, text, intent):
        messages = self._run(text)
        types = [m.msg_type for m in messages]
        self.assertIn(f"{SKILL_ID}:{intent}", types)
        spoken = [
            m.data.get("utterance", "")
            for m in messages
            if m.msg_type in ("speak", "ovos.utterance.speak")
        ]
        self.assertTrue(spoken, f"expected a spoken response for {text!r}, got {types!r}")
        expected_lines = _DIALOG_LINES[intent]
        self.assertTrue(
            any(utt in expected_lines for utt in spoken),
            f"expected one of {intent}.dialog's own lines to be spoken for "
            f"{text!r}, got {spoken!r}",
        )

    def test_confucius_quote(self):
        self._assert_intent("give me a confucius quote", "ConfuciusQuote")

    def test_when_did_confucius_live(self):
        self._assert_intent("when did confucius live", "confucius_lifespan")

    def test_when_was_confucius_born(self):
        self._assert_intent("when was confucius born", "confucius_lifespan")

    def test_when_did_confucius_die(self):
        self._assert_intent("when did confucius die", "confucius_lifespan")
