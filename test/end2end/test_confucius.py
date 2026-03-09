"""
End-to-end tests for ovos-skill-confucius-quotes.

Covers:
- Adapt intent: ConfuciusQuote ("tell me a confucius quote")
- Adapt intent: ConfuciusBirth ("when was confucius born")
- Adapt intent: ConfuciusDeath ("when did confucius die")
- Padatious intent: who.intent ("who is confucius")
"""
from unittest import TestCase

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovos_utils.log import LOG

from ovoscope import ADAPT_PIPELINE, End2EndTest, get_minicroft
from ovoscope import PADATIOUS_PIPELINE


SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"


class TestConfuciusAdapt(TestCase):

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _session(self, pipeline):
        s = Session("test-confucius-adapt")
        s.lang = "en-US"
        s.pipeline = pipeline
        return s

    def test_quote_intent(self):
        session = self._session(ADAPT_PIPELINE)
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["tell me a confucius quote"], "lang": session.lang},
                          {"session": session.serialize(), "source": "A", "destination": "B"})

        test = End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[SKILL_ID],
            source_message=message,
            ignore_messages=["ovos.gui.screen.close"],
            expected_messages=[
                message,
                Message(f"{SKILL_ID}.activate",
                        data={},
                        context={"skill_id": SKILL_ID}),
                Message(f"{SKILL_ID}:ConfuciusQuote",
                        data={"utterance": "tell me a confucius quote", "lang": "en-US"},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.start",
                        data={"name": "ConfuciusQuotesSkill.handle_quote"},
                        context={"skill_id": SKILL_ID}),
                Message("speak",
                        data={"lang": "en-US",
                              "expect_response": False,
                              "meta": {"skill": SKILL_ID}},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.complete",
                        data={"name": "ConfuciusQuotesSkill.handle_quote"},
                        context={"skill_id": SKILL_ID}),
                Message("ovos.utterance.handled",
                        data={"name": "ConfuciusQuotesSkill.handle_quote"},
                        context={"skill_id": SKILL_ID}),
            ]
        )
        test.execute(timeout=10)

    def test_birth_intent(self):
        session = self._session(ADAPT_PIPELINE)
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["when was confucius born"], "lang": session.lang},
                          {"session": session.serialize(), "source": "A", "destination": "B"})

        test = End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[SKILL_ID],
            source_message=message,
            ignore_messages=["ovos.gui.screen.close"],
            expected_messages=[
                message,
                Message(f"{SKILL_ID}.activate",
                        data={},
                        context={"skill_id": SKILL_ID}),
                Message(f"{SKILL_ID}:ConfuciusBirth",
                        data={"utterance": "when was confucius born", "lang": "en-US"},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.start",
                        data={"name": "ConfuciusQuotesSkill.handle_birth"},
                        context={"skill_id": SKILL_ID}),
                Message("speak",
                        data={"lang": "en-US",
                              "expect_response": False,
                              "meta": {"skill": SKILL_ID}},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.complete",
                        data={"name": "ConfuciusQuotesSkill.handle_birth"},
                        context={"skill_id": SKILL_ID}),
                Message("ovos.utterance.handled",
                        data={"name": "ConfuciusQuotesSkill.handle_birth"},
                        context={"skill_id": SKILL_ID}),
            ]
        )
        test.execute(timeout=10)

    def test_death_intent(self):
        session = self._session(ADAPT_PIPELINE)
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["when did confucius die"], "lang": session.lang},
                          {"session": session.serialize(), "source": "A", "destination": "B"})

        test = End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[SKILL_ID],
            source_message=message,
            ignore_messages=["ovos.gui.screen.close"],
            expected_messages=[
                message,
                Message(f"{SKILL_ID}.activate",
                        data={},
                        context={"skill_id": SKILL_ID}),
                Message(f"{SKILL_ID}:ConfuciusDeath",
                        data={"utterance": "when did confucius die", "lang": "en-US"},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.start",
                        data={"name": "ConfuciusQuotesSkill.handle_death"},
                        context={"skill_id": SKILL_ID}),
                Message("speak",
                        data={"lang": "en-US",
                              "expect_response": False,
                              "meta": {"skill": SKILL_ID}},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.complete",
                        data={"name": "ConfuciusQuotesSkill.handle_death"},
                        context={"skill_id": SKILL_ID}),
                Message("ovos.utterance.handled",
                        data={"name": "ConfuciusQuotesSkill.handle_death"},
                        context={"skill_id": SKILL_ID}),
            ]
        )
        test.execute(timeout=10)


class TestConfuciusPadatious(TestCase):

    @classmethod
    def setUpClass(cls):
        LOG.set_level("WARNING")
        cls.minicroft = get_minicroft([SKILL_ID])

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _session(self, pipeline):
        s = Session("test-confucius-padatious")
        s.lang = "en-US"
        s.pipeline = pipeline
        return s

    def test_who_intent(self):
        session = self._session(PADATIOUS_PIPELINE)
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["who is confucius"], "lang": session.lang},
                          {"session": session.serialize(), "source": "A", "destination": "B"})

        test = End2EndTest(
            minicroft=self.minicroft,
            skill_ids=[SKILL_ID],
            source_message=message,
            ignore_messages=["ovos.gui.screen.close"],
            expected_messages=[
                message,
                Message(f"{SKILL_ID}.activate",
                        data={},
                        context={"skill_id": SKILL_ID}),
                Message(f"{SKILL_ID}:who.intent",
                        data={"utterance": "who is confucius", "lang": "en-US"},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.start",
                        data={"name": "ConfuciusQuotesSkill.handle_who"},
                        context={"skill_id": SKILL_ID}),
                Message("speak",
                        data={"lang": "en-US",
                              "expect_response": False,
                              "meta": {"skill": SKILL_ID}},
                        context={"skill_id": SKILL_ID}),
                Message("mycroft.skill.handler.complete",
                        data={"name": "ConfuciusQuotesSkill.handle_who"},
                        context={"skill_id": SKILL_ID}),
                Message("ovos.utterance.handled",
                        data={"name": "ConfuciusQuotesSkill.handle_who"},
                        context={"skill_id": SKILL_ID}),
            ]
        )
        test.execute(timeout=10)
