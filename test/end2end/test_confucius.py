"""
End-to-end tests for ovos-skill-confucius-quotes.

Covers all 5 intent handlers in English plus language-specific tests
for pt-pt, de-de, and es-es using MiniCroft's secondary_langs support.

Three engine classes test each Padatious-style intent:
- TestConfuciusPadatiousEN  — uses PADATIOUS_PIPELINE (C engine, skip if not installed)
- TestConfuciusPadaciosaEN  — uses PADACIOSO_PIPELINE (pure Python, always available)
- TestConfuciusM2VEN        — uses M2V_PIPELINE (vector engine, skip if not installed)

Intents:
- Adapt: ConfuciusQuote  (confucius + quote/say/saying)
- Adapt: ConfuciusLive   (confucius + when + live/alive)
- Adapt: ConfuciusBirth  (confucius + birth/birthday/born)
- Adapt: ConfuciusDeath  (confucius + death/die)
- Padatious: who.intent  ("who is confucius" / "who was confucius")
"""
import os
import unittest

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovos_utils.log import LOG

from ovoscope import (
    ADAPT_PIPELINE,
    PADATIOUS_PIPELINE,
    PADACIOSO_PIPELINE,
    M2V_PIPELINE,
    End2EndTest,
    get_minicroft,
    is_pipeline_available,
)


SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# ovos.gui.screen.close is not in ovoscope's GUI_IGNORED list.
# intent.service.adapt.manifest.get and intent.service.padatious.manifest.get
# are emitted by ovos-m2v-pipeline's background intent-sync thread (3-second
# debounce after startup) and can appear at any point during early tests.
EXTRA_IGNORED = [
    "ovos.gui.screen.close",
    # M2V background intent-sync thread fires these manifest messages
    # (request + response) 3 seconds after startup, during early tests.
    "intent.service.adapt.manifest.get",
    "intent.service.adapt.manifest",
    "intent.service.padatious.manifest.get",
    "intent.service.padatious.manifest",
]


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
    """Standard Padatious/Padacioso expected message sequence."""
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


def _make_exact_match_test(minicroft, pipeline, utterance, lang="en-US"):
    """Build an End2EndTest for the who.intent exact-match intent."""
    sess = _session(pipeline, lang=lang)
    msg = _utterance_msg(utterance, sess)
    return End2EndTest(
        minicroft=minicroft,
        skill_ids=[SKILL_ID],
        source_message=msg,
        ignore_messages=EXTRA_IGNORED,
        expected_messages=[msg] + _padatious_expected(utterance, lang, "handle_who"),
    )


# ──────────────────────────────────────────────────────────────────────
# English tests — all 5 Adapt intents
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusAdaptEN(unittest.TestCase):
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


# ──────────────────────────────────────────────────────────────────────
# who.intent — Padacioso (pure Python, always available)
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusPadaciosaEN(unittest.TestCase):
    """who.intent via Padacioso (pure Python engine, no swig required)."""

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def test_who_intent(self):
        test = _make_exact_match_test(self.minicroft, PADACIOSO_PIPELINE, "who is confucius")
        test.execute(timeout=10)

    def test_who_intent_past_tense(self):
        test = _make_exact_match_test(self.minicroft, PADACIOSO_PIPELINE, "who was confucius")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# who.intent — Padatious (C extension engine, optional)
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusPadatiousEN(unittest.TestCase):
    """who.intent via Padatious (C extension engine).

    Skipped when ovos-padatious-pipeline-plugin is not installed.
    Add 'ovos-padatious-pipeline-plugin' to [test] deps to enable.
    """

    @classmethod
    def setUpClass(cls):
        if not is_pipeline_available(PADATIOUS_PIPELINE):
            raise unittest.SkipTest(
                "ovos-padatious-pipeline-plugin not installed — "
                "add it to [test] deps or install manually"
            )
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "minicroft"):
            cls.minicroft.stop()

    def test_who_intent(self):
        test = _make_exact_match_test(self.minicroft, PADATIOUS_PIPELINE, "who is confucius")
        test.execute(timeout=10)

    def test_who_intent_past_tense(self):
        test = _make_exact_match_test(self.minicroft, PADATIOUS_PIPELINE, "who was confucius")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# who.intent — M2V vector pipeline (optional)
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusM2VEN(unittest.TestCase):
    """who.intent via Model2Vec vector pipeline (optional).

    Skipped when ovos-m2v-pipeline is not installed.
    Add 'ovos-m2v-pipeline' to [test] deps to enable.
    """

    # The multilingual model covers all OVOS skill intent names regardless of
    # language; a language-specific model (e.g. Portuguese-only) won't contain
    # English intent names in its classes_ and will always return no match.
    _M2V_MULTILINGUAL_MODEL = (
        "Jarbas/ovos-model2vec-intents-distiluse-base-multilingual-cased-v2"
    )

    @classmethod
    def _multilingual_model_cached(cls) -> bool:
        """Return True if the multilingual model is in the HuggingFace cache."""
        import os
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
        repo_dir = cls._M2V_MULTILINGUAL_MODEL.replace("/", "--").replace("/", "--")
        model_dir = f"models--{cls._M2V_MULTILINGUAL_MODEL.replace('/', '--')}"
        return os.path.isdir(os.path.join(hf_cache, model_dir))

    @classmethod
    def setUpClass(cls):
        if not is_pipeline_available(M2V_PIPELINE):
            raise unittest.SkipTest(
                "ovos-m2v-pipeline not installed — "
                "add it to [test] deps or install manually"
            )
        if not cls._multilingual_model_cached():
            raise unittest.SkipTest(
                f"Multilingual M2V model not cached locally — "
                f"run: python -c \"from model2vec.inference import StaticModelPipeline; "
                f"StaticModelPipeline.from_pretrained('{cls._M2V_MULTILINGUAL_MODEL}')\" "
                f"to download it"
            )
        LOG.set_level("WARNING")
        # Force the multilingual model regardless of what mycroft.conf says,
        # so tests are reproducible even when the user has a language-specific
        # model configured locally.  pipeline_config patches
        # Configuration()["intents"]["ovos_m2v_pipeline"] before the M2V
        # pipeline plugin is instantiated in super().__init__().
        cls.minicroft = get_minicroft(
            [SKILL_ID],
            pipeline_config={"ovos_m2v_pipeline": {"model": cls._M2V_MULTILINGUAL_MODEL}},
        )
        # M2V pipeline syncs intents in a background thread with a 3-second
        # debounce followed by a 5-second query timeout. Wait for the sync to
        # complete so that self.intents is populated before the first test runs.
        import time
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "minicroft"):
            cls.minicroft.stop()

    def test_who_intent(self):
        test = _make_exact_match_test(self.minicroft, M2V_PIPELINE, "who is confucius")
        test.execute(timeout=10)

    def test_who_intent_past_tense(self):
        test = _make_exact_match_test(self.minicroft, M2V_PIPELINE, "who was confucius")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# Multilingual tests — use secondary_langs to register non-English vocab
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusMultilingual(unittest.TestCase):
    """Adapt + exact-match intents in pt-PT, de-DE, and es-ES.

    Uses MiniCroft's secondary_langs parameter to register vocab
    for all target languages at startup.
    Uses Padacioso for exact-match intents (always available).
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
        test = _make_exact_match_test(self.minicroft, PADACIOSO_PIPELINE,
                                      "quem é confúcio", lang="pt-PT")
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
        test = _make_exact_match_test(self.minicroft, PADACIOSO_PIPELINE,
                                      "Wer ist Konfuzius", lang="de-DE")
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
        test = _make_exact_match_test(self.minicroft, PADACIOSO_PIPELINE,
                                      "Quién es Confucio", lang="es-ES")
        test.execute(timeout=10)


# ──────────────────────────────────────────────────────────────────────
# Fixture tests — replay from recorded JSON (Pattern 4)
# ──────────────────────────────────────────────────────────────────────


class TestConfuciusFixtures(unittest.TestCase):
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
