"""Adapt-less end-to-end intent routing tests for the en-US locale.

These mirror ``test_intents_en_us.py`` but drop every Adapt pipeline stage
from the session pipeline, leaving only Padatious/Padacioso. They prove the
``ConfuciusQuote``/``confucius_lifespan``
intents are resolved from the ``.intent`` files under ``locale/en-US/intents/``
rather than from the (now removed) ``IntentBuilder().require(...)`` Adapt
definitions.
"""
import unittest

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"


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
        self.assertTrue(any("speak" in t for t in types))

    def test_confucius_quote(self):
        self._assert_intent("give me a confucius quote", "ConfuciusQuote")

    def test_when_did_confucius_live(self):
        self._assert_intent("when did confucius live", "confucius_lifespan")

    def test_when_was_confucius_born(self):
        self._assert_intent("when was confucius born", "confucius_lifespan")

    def test_when_did_confucius_die(self):
        self._assert_intent("when did confucius die", "confucius_lifespan")
