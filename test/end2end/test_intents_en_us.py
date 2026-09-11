"""End-to-end intent routing tests for the en-US locale.

Each canonical utterance is fired through a real MiniCroft and asserted to
route to the expected intent handler AND to speak a dialog line drawn from
that intent's own ``.dialog`` file. The expected line set is read directly
from the locale file on disk, independent of the skill handler under test,
so a handler that speaks the wrong dialog (or the right dialog for a
different intent) fails here even though it still emits a ``speak`` message
and still matches the correct intent name.
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


# Read once, directly from the shipped dialog files -- never from a captured
# bus message -- so these sets are independent of the code under test.
QUOTE_LINES = _dialog_lines("quote")
LIFESPAN_LINES = _dialog_lines("lifespan")
WHO_LINES = _dialog_lines("confucius")

_DIALOG_LINES = {
    "ConfuciusQuote": QUOTE_LINES,
    "who": WHO_LINES,
    "confucius_lifespan": LIFESPAN_LINES,
}


class TestConfuciusIntentsEnUS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _run(self, text):
        session = Session("test-session")
        session.pipeline = [
            "ovos-adapt-pipeline-plugin-high",
            "ovos-padatious-pipeline-plugin-high",
            "ovos-padacioso-pipeline-plugin-high",
            "ovos-adapt-pipeline-plugin-medium",
            "ovos-padacioso-pipeline-plugin-medium",
            "ovos-adapt-pipeline-plugin-low",
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
        self._assert_intent("tell me a confucius quote", "ConfuciusQuote")

    def test_who_was_confucius(self):
        self._assert_intent("who was confucius", "who")

    def test_when_did_confucius_live(self):
        self._assert_intent("when did confucius live", "confucius_lifespan")

    def test_when_was_confucius_born(self):
        self._assert_intent("when was confucius born", "confucius_lifespan")

    def test_when_did_confucius_die(self):
        self._assert_intent("when did confucius die", "confucius_lifespan")

    def test_when_was_confucius_last_alive(self):
        self._assert_intent("when was confucius last alive", "confucius_lifespan")

    def test_is_confucius_still_alive(self):
        self._assert_intent("is confucius still alive", "confucius_lifespan")
