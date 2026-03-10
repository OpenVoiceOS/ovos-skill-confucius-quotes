"""
End-to-end tests for ovos-skill-confucius-quotes.

Covers all 5 intent handlers in English, plus language-specific tests
for pt-pt, de-de, and es-es using MiniCroft's secondary_langs support.

Intents:
- Adapt: ConfuciusQuote  (confucius + quote/say/saying)
- Adapt: ConfuciusLive   (confucius + when + live/alive)
- Adapt: ConfuciusBirth  (confucius + birth/birthday/born)
- Adapt: ConfuciusDeath  (confucius + death/die)
- Padatious: who.intent  ("who is confucius" / "who was confucius")
"""
import os
from unittest import TestCase

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovos_utils.log import LOG

from ovoscope import ADAPT_PIPELINE, PADATIOUS_PIPELINE, End2EndTest, get_minicroft


SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# ovos.gui.screen.close is not in ovoscope's GUI_IGNORED list
EXTRA_IGNORED = ["ovos.gui.screen.close"]


def _session(pipeline, lang="en-US", session_id="test-confucius"):
    s = Session(session_id)
    s.lang = lang
    s.pipeline = pipeline
    return s


def _utterance_msg(text, session):
    return Message("recognizer_loop:utterance",
                   {"utterances": [text], "lang": session.lang},
                   {"session": session.serialize(), "source": "A", "destination": "B"})


# Maps handler names to their dialog file names
HANDLER_DIALOG = {
    "handle_quote": "quote",
    "handle_live": "live",
    "handle_birth": "birth",
    "handle_death": "death",
    "handle_who": "confucius",
}


def _adapt_expected(utterance, lang, intent_name, handler_name):
    """Standard Adapt expected message sequence."""
    dialog = HANDLER_DIALOG[handler_name]
    return [
        Message(f"{SKILL_ID}.activate",
                data={},
                context={"skill_id": SKILL_ID}),
        Message(f"{SKILL_ID}:{intent_name}",
                data={"utterance": utterance, "lang": lang},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.start",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
        Message("speak",
                data={"lang": lang,
                      "expect_response": False,
                      "meta": {"dialog": dialog, "data": {}, "skill": SKILL_ID}},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.complete",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
        Message("ovos.utterance.handled",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
    ]


def _padatious_expected(utterance, lang, handler_name):
    """Standard Padatious expected message sequence."""
    dialog = HANDLER_DIALOG[handler_name]
    return [
        Message(f"{SKILL_ID}.activate",
                data={},
                context={"skill_id": SKILL_ID}),
        Message(f"{SKILL_ID}:who.intent",
                data={"utterance": utterance, "lang": lang},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.start",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
        Message("speak",
                data={"lang": lang,
                      "expect_response": False,
                      "meta": {"dialog": dialog, "data": {}, "skill": SKILL_ID}},
                context={"skill_id": SKILL_ID}),
        Message("mycroft.skill.handler.complete",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
        Message("ovos.utterance.handled",
                data={"name": f"ConfuciusQuotesSkill.{handler_name}"},
                context={"skill_id": SKILL_ID}),
    ]


def _make_adapt_test(minicroft, utterance, intent_name, handler_name, lang="en-US"):
    """Build an End2EndTest for an Adapt intent."""
    sess = _session(ADAPT_PIPELINE, lang=lang)
    msg = _utterance_msg(utterance, sess)
    return End2EndTest(
        minicroft=minicroft,
        skill_ids=[SKILL_ID],
        source_message=msg,
        ignore_messages=EXTRA_IGNORED,
        expected_messages=[msg] + _adapt_expected(utterance, lang, intent_name, handler_name),
    )


def _make_padatious_test(minicroft, utterance, lang="en-US"):
    """Build an End2EndTest for the who.intent Padatious intent."""
    sess = _session(PADATIOUS_PIPELINE, lang=lang)
    msg = _utterance_msg(utterance, sess)
    return End2EndTest(
        minicroft=minicroft,
        skill_ids=[SKILL_ID],
        source_message=msg,
        ignore_messages=EXTRA_IGNORED,
        expected_messages=[msg] + _padatious_expected(utterance, lang, "handle_who"),
    )


# ──────────────────────────────────────────────────────────────────────
# English tests — all 5 intents with alternative phrasings
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusAdaptEN(TestCase):
    """Adapt intents in en-US."""

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    # --- ConfuciusQuote ---

    def test_quote_intent(self):
        test = _make_adapt_test(self.minicroft,
                                "tell me a confucius quote",
                                "ConfuciusQuote", "handle_quote")
        test.execute(timeout=10)

    def test_quote_intent_saying(self):
        test = _make_adapt_test(self.minicroft,
                                "give me a confucius saying",
                                "ConfuciusQuote", "handle_quote")
        test.execute(timeout=10)

    # --- ConfuciusLive ---

    def test_live_intent(self):
        test = _make_adapt_test(self.minicroft,
                                "when did confucius live",
                                "ConfuciusLive", "handle_live")
        test.execute(timeout=10)

    def test_live_intent_alive(self):
        test = _make_adapt_test(self.minicroft,
                                "when was confucius alive",
                                "ConfuciusLive", "handle_live")
        test.execute(timeout=10)

    # --- ConfuciusBirth ---

    def test_birth_intent(self):
        test = _make_adapt_test(self.minicroft,
                                "when was confucius born",
                                "ConfuciusBirth", "handle_birth")
        test.execute(timeout=10)

    def test_birth_intent_birthday(self):
        test = _make_adapt_test(self.minicroft,
                                "confucius birthday",
                                "ConfuciusBirth", "handle_birth")
        test.execute(timeout=10)

    # --- ConfuciusDeath ---

    def test_death_intent(self):
        test = _make_adapt_test(self.minicroft,
                                "when did confucius die",
                                "ConfuciusDeath", "handle_death")
        test.execute(timeout=10)


class TestConfuciusPadatiousEN(TestCase):
    """Padatious intents in en-US."""

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def test_who_intent(self):
        test = _make_padatious_test(self.minicroft, "who is confucius")
        test.execute(timeout=10)

    def test_who_intent_past_tense(self):
        test = _make_padatious_test(self.minicroft, "who was confucius")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# Multilingual tests — use secondary_langs to register non-English vocab
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusMultilingual(TestCase):
    """Adapt + Padatious intents in pt-PT, de-DE, and es-ES.

    Uses MiniCroft's secondary_langs parameter to register vocab
    for all target languages at startup.
    """

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft(
            [SKILL_ID],
            secondary_langs=["pt-PT", "de-DE", "es-ES"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    # --- Portuguese (pt-PT) ---
    # confucius.voc: "Confúcio", quote.voc: "citação"/"diria"/"ditado"

    def test_quote_intent_pt(self):
        test = _make_adapt_test(self.minicroft,
                                "Confúcio citação",
                                "ConfuciusQuote", "handle_quote",
                                lang="pt-PT")
        test.execute(timeout=10)

    def test_who_intent_pt(self):
        test = _make_padatious_test(self.minicroft,
                                    "quem é confúcio",
                                    lang="pt-PT")
        test.execute(timeout=10)

    # --- German (de-DE) ---
    # confucius.voc: "Konfuzius", quote.voc: "Zitat"/"sagt"/"sagte"

    def test_quote_intent_de(self):
        test = _make_adapt_test(self.minicroft,
                                "Konfuzius Zitat",
                                "ConfuciusQuote", "handle_quote",
                                lang="de-DE")
        test.execute(timeout=10)

    def test_who_intent_de(self):
        test = _make_padatious_test(self.minicroft,
                                    "Wer ist Konfuzius",
                                    lang="de-DE")
        test.execute(timeout=10)

    # --- Spanish (es-ES) ---
    # confucius.voc: "Confucio", quote.voc: "cita"/"decir"/"dicho"

    def test_quote_intent_es(self):
        test = _make_adapt_test(self.minicroft,
                                "Confucio cita",
                                "ConfuciusQuote", "handle_quote",
                                lang="es-ES")
        test.execute(timeout=10)

    def test_who_intent_es(self):
        test = _make_padatious_test(self.minicroft,
                                    "Quién es Confucio",
                                    lang="es-ES")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# Fixture tests — replay from recorded JSON (Pattern 4)
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusFixtures(TestCase):
    """Replay tests from pre-recorded JSON fixtures.

    Fixtures are generated by running:
        python test/end2end/generate_fixtures.py
    """

    def _fixture(self, name):
        path = os.path.join(FIXTURES_DIR, name)
        if not os.path.exists(path):
            self.skipTest(f"fixture not found: {name} — run generate_fixtures.py")
        return path

    def _load_fixture(self, name):
        test = End2EndTest.from_path(self._fixture(name))
        test.ignore_messages += EXTRA_IGNORED
        # Session context contains timestamps (active_skills activation time)
        # and dialog rendering is non-deterministic (random quote selection),
        # so disable strict data and context checks for fixture replay.
        # The fixture still validates message types, count, and routing.
        test.test_msg_context = False
        test.test_msg_data = False
        return test

    def test_quote_adapt_fixture(self):
        self._load_fixture("quote_adapt_en.json").execute(timeout=10)

    def test_who_padatious_fixture(self):
        self._load_fixture("who_padatious_en.json").execute(timeout=10)

    def test_live_adapt_fixture(self):
        self._load_fixture("live_adapt_en.json").execute(timeout=10)
