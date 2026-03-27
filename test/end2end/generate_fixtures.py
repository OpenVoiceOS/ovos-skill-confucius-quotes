"""Record ovoscope fixtures for ovos-skill-confucius-quotes.

Run once to generate JSON fixtures, then commit them.
Tests in TestConfuciusFixtures replay these fixtures.

Usage:
    python test/end2end/generate_fixtures.py
"""
import os

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovos_utils.log import LOG

from ovoscope import ADAPT_PIPELINE, PADATIOUS_PIPELINE, End2EndTest

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
EXTRA_IGNORED = ["ovos.gui.screen.close"]


def _record(utterance, lang, pipeline, fixture_name):
    session = Session("fixture-recording")
    session.lang = lang
    session.pipeline = pipeline

    message = Message(
        "recognizer_loop:utterance",
        {"utterances": [utterance], "lang": lang},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )

    test = End2EndTest.from_message(
        message=message,
        skill_ids=[SKILL_ID],
        ignore_messages=EXTRA_IGNORED,
        timeout=20,
    )

    path = os.path.join(FIXTURES_DIR, fixture_name)
    test.save(path, anonymize=True)
    print(f"  saved: {path} ({len(test.expected_messages)} messages)")


def main():
    LOG.set_level("WARNING")
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    print("Recording fixtures...")

    _record("tell me a confucius quote", "en-US",
            ADAPT_PIPELINE, "quote_adapt_en.json")

    _record("who is confucius", "en-US",
            PADATIOUS_PIPELINE, "who_padatious_en.json")

    _record("when did confucius live", "en-US",
            ADAPT_PIPELINE, "live_adapt_en.json")

    print("Done.")


if __name__ == "__main__":
    main()
