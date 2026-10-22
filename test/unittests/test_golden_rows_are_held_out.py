"""No golden or negative test row is a sentence a template spells out.

The golden test runs the m2v prototype engine, which is built at boot from
the skill's own templates. A test row that is also a template sentence
matches because the engine has seen it, so it no longer measures how well the
engine generalises.
"""
import json
import re
import unicodedata
from pathlib import Path

import pytest
from ovos_spec_tools.expansion import expand

ROOT = Path(__file__).resolve().parents[2]
LOCALE = ROOT / "locale"
END2END = ROOT / "test" / "end2end"
LANGS = sorted(d.name for d in LOCALE.iterdir() if d.is_dir() and any(d.rglob("*.intent")))


def _fold(sentence):
    sentence = unicodedata.normalize("NFC", sentence).lower()
    sentence = re.sub(r"[^\w\s]", " ", sentence)
    return re.sub(r"\s+", " ", sentence).strip()


def _template_sentences(lang):
    vocs = {}
    for path in (LOCALE / lang).rglob("*.voc"):
        vocs[path.stem] = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
                           if line.strip() and not line.startswith("#")]
    sentences = set()
    for path in (LOCALE / lang).rglob("*.intent"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                sentences.update(_fold(s) for s in expand(line.strip(), vocs))
    return sentences


def _rows(prefix, lang):
    path = END2END / f"{prefix}_{lang}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line)["utterance"] for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


@pytest.mark.parametrize("lang", LANGS)
def test_no_test_row_is_a_template_sentence(lang):
    sentences = _template_sentences(lang)
    leaked = [u for prefix in ("golden_utterances", "negative_utterances")
              for u in _rows(prefix, lang) if _fold(u) in sentences]
    assert leaked == []


TOPIC_SENTENCES = {
    "da-DK": "hvad sagde confucius om livet",
    "fa-IR": "کنفوسیوس درباره زندگی چه گفته است",
    "fr-FR": "qu'a dit confucius sur la sagesse",
    "gl-ES": "que dixo confucio sobre a vida",
    "nl-NL": "wat zei confucius over het leven",
    "ru-RU": "что говорил конфуций о жизни",
    "sv-SE": "vad sa konfucius om livet",
}


@pytest.mark.parametrize("lang", sorted(TOPIC_SENTENCES))
def test_the_natural_about_a_topic_question_is_a_quote_template(lang):
    """"What did Confucius say about life" is the request the quote templates
    exist for, so a template spells it out."""
    quote = set()
    for line in (LOCALE / lang / "intents" / "confucius_quote.intent").read_text(
            encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            quote.update(_fold(s) for s in expand(line.strip()))
    assert _fold(TOPIC_SENTENCES[lang]) in quote
