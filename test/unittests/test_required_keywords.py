"""Every intent of the skill is anchored on the name of Confucius by a `.required` file.

OVOS-INTENT-2 4.5: an intent is rejected when none of its required keywords
occurs in the utterance. Without the name, a general question about a person,
a quote or a lifespan never reaches these intents.
"""
import json
from pathlib import Path

import pytest
from ovos_spec_tools.resources import LocaleResources, required_keywords_reject

ROOT = Path(__file__).parents[2]
LOCALE_DIR = ROOT / "locale"
GOLDEN_DIR = ROOT / "test" / "end2end"
INTENTS = {"confucius_quote": "confucius_quote",
           "confucius_lifespan": "confucius_lifespan",
           "who": "who"}
LANGS = sorted(p.name for p in LOCALE_DIR.iterdir() if p.is_dir())
CASES = [(intent, lang) for intent in INTENTS for lang in LANGS]
RESOURCES = LocaleResources(str(LOCALE_DIR))


def _keywords(intent, lang):
    return RESOURCES.load_required_keywords(intent, lang)


def _golden(lang):
    path = GOLDEN_DIR / f"golden_utterances_{lang}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def test_locales_found():
    assert LANGS


@pytest.mark.parametrize("intent,lang", CASES)
def test_locale_has_a_required_file(intent, lang):
    assert _keywords(intent, lang), f"{lang}: no required keywords for {intent}"


@pytest.mark.parametrize("intent,lang", CASES)
def test_every_intent_sample_contains_a_keyword(intent, lang):
    keywords = _keywords(intent, lang)
    dead = [s for s in RESOURCES.load_intent(intent, lang)
            if required_keywords_reject(s, keywords)]
    assert not dead, f"samples the requirement rejects: {dead[:5]}"


@pytest.mark.parametrize("intent,lang", CASES)
def test_golden_positives_contain_a_keyword(intent, lang):
    keywords = _keywords(intent, lang)
    rows = [r["utterance"] for r in _golden(lang) if r["intent_label"] == INTENTS[intent]]
    assert rows
    rejected = [u for u in rows if required_keywords_reject(u, keywords)]
    assert not rejected, f"golden rows with no required keyword: {rejected}"


@pytest.mark.parametrize("intent", INTENTS)
def test_general_question_is_rejected(intent):
    assert required_keywords_reject("who is albert einstein", _keywords(intent, "en-US"))
