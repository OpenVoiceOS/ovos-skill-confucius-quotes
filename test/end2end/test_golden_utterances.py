"""Golden rows in every locale route to their intent on the m2v pipeline.

For each ``golden_utterances_<lang>.jsonl`` in this directory, one MiniCroft
loads the real skill in that language on the m2v prototype pipeline, the
model2vec engine built at boot from the skill's own ``.intent`` files. Each
row's utterance goes through that pipeline's high, medium and low tiers in
order, and the row passes when the first tier to match names its
``intent_label``. The engine embeds the utterance, so a row that no template
spells out word for word still matches when it means the same thing.

Each ``negative_utterances_<lang>.jsonl`` holds requests for other skills.
They run on the same pipeline and must not match any intent of this skill.

Each locale must match at least ``MIN_MATCH_RATE`` of its golden rows, and at
least ``MIN_MATCHED_ROWS_PER_INTENT`` rows of each intent. A negative row that
matches this skill fails the locale, unless ``NEGATIVE_KNOWN_CLAIMS`` lists
that claim. All rows run, including rows marked ``needs_manual`` or
``machine_generated``, and the test prints every row that misses with the
intent that matched instead.
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovoscope import M2V_PUBLISHED_MODEL, get_m2v_minicroft
from ovoscope.golden_minicroft import warm_m2v_models

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
M2V_PROTOTYPE = "ovos-m2v-prototype-pipeline"
TIERS = ("high", "medium", "low")
# m2v gives some rows a different answer on each boot, so the test gates on
# the share of rows that match per locale, not on each row.
MIN_MATCH_RATE = 0.8
# A locale also fails when any of its intents has fewer matched rows than this.
MIN_MATCHED_ROWS_PER_INTENT = 1
# Locales below MIN_MATCH_RATE, mapped to the rate measured as the worst of
# three runs and the reason. For a listed locale the rate check is an xfail,
# but the locale still fails when an intent is below MIN_MATCHED_ROWS_PER_INTENT,
# when its rate drops more than GAP_TOLERANCE below the measured rate, or when
# it reaches MIN_MATCH_RATE: remove the entry then.
GOLDEN_LOCALE_GAPS = {
    "es-CO": (0.786, "3 of 14 rows miss: 'quiero oír un proverbio de confucio' "
                     "matches nothing; 'háblame de confucio' and 'qué sabes de "
                     "confucio' land on confucius_quote; "
                     "measured on the prototype engine; remove when the rows match"),
    "fr-FR": (0.786, "3 of 14 rows miss: \"j'aimerais entendre un proverbe de "
                     "confucius\" matches nothing; \"qu'est-ce que tu sais sur "
                     "confucius\" lands on confucius_quote; \"est-ce que confucius "
                     "vit encore aujourd'hui\" lands on who; "
                     "measured on the prototype engine; remove when the rows match"),
    "ru-RU": (0.786, "3 of 14 rows miss: two match nothing and 'что тебе "
                     "известно про конфуция' lands on confucius_quote; "
                     "measured on the prototype engine; remove when the rows "
                     "match"),
}
GAP_TOLERANCE = 0.10
END2END_DIR = Path(__file__).parent
# Locales whose negative rows the published m2v model cannot separate from
# this skill's intents, mapped to the measured reason.
NEGATIVE_ENGINE_GAPS = {}
# Negative rows that m2v claimed for this skill in two separate runs. A listed
# claim is allowed, not required, so a row that flips between boots does not
# fail the test. Any other claim fails the locale. Prototype mode weighs the
# question shape over the name, so "when was <someone else> born" lands on
# confucius_lifespan.
NEGATIVE_KNOWN_CLAIMS = {
    "ca-ES": {"quan va néixer picasso": "confucius_lifespan"},
    "da-DK": {"hvornår blev h c andersen født": "confucius_lifespan"},
    "de-DE": {"wann wurde goethe geboren": "confucius_lifespan"},
    "en-US": {"when was abraham lincoln born": "confucius_lifespan"},
    "fr-FR": {"quand est né victor hugo": "confucius_lifespan"},
    "nl-NL": {"wanneer werd rembrandt geboren": "confucius_lifespan"},
    "pl-PL": {"kiedy urodził się mikołaj kopernik": "confucius_lifespan"},
    "pt-BR": {"quando nasceu machado de assis": "confucius_lifespan"},
    "ru-RU": {
        "какая завтра будет погода": "confucius_lifespan",
        "расскажи анекдот": "confucius_quote",
        "когда родился пушкин": "confucius_lifespan",
    },
}
# Negative rows the prototype engine claims for this skill on every boot
# (three runs each): "when was <someone else> born" is read as the question
# shape of confucius_lifespan. Unlike NEGATIVE_KNOWN_CLAIMS, each claim here
# must occur, so a claim that stops occurring fails the test and the entry
# is removed.
NEGATIVE_PUBLISHED_MODEL_CLAIMS = {
    "es-CO": {"cuándo nació gabriel garcía márquez": "confucius_lifespan"},
    "es-ES": {"cuándo nació cervantes": "confucius_lifespan"},
    "gl-ES": {"cando naceu rosalía de castro": "confucius_lifespan"},
    "pt-PT": {"quando nasceu camões": "confucius_lifespan"},
    "sv-SE": {"när föddes astrid lindgren": "confucius_lifespan"},
}


def _rows_by_lang(prefix):
    rows = {}
    for path in sorted(END2END_DIR.glob(f"{prefix}_*.jsonl")):
        lang = path.stem.removeprefix(f"{prefix}_")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                row = json.loads(line)
                assert row["lang"] == lang, f"{path.name}:{number} has lang {row['lang']!r}"
                rows.setdefault(lang, []).append(row)
    return rows


ROWS = _rows_by_lang("golden_utterances")
NEGATIVE_ROWS = _rows_by_lang("negative_utterances")


def _matched_intent(engine, utterance, lang):
    message = Message("recognizer_loop:utterance",
                      {"utterances": [utterance], "lang": lang}, {"lang": lang})
    match = next(filter(None, (getattr(engine, f"match_{tier}")([utterance], lang, message)
                               for tier in TIERS)), None)
    return match.match_type if match else None


def _match_all(lang, rows):
    """Boot the skill on m2v in ``lang`` and return the intent each row matches."""
    minicroft = get_m2v_minicroft([SKILL_ID], model=M2V_PUBLISHED_MODEL,
                                  lang=lang, classifier=False)
    try:
        warm_m2v_models(minicroft)
        engine = minicroft.intents.pipeline_plugins[M2V_PROTOTYPE]
        return [_matched_intent(engine, row["utterance"], lang) for row in rows]
    finally:
        minicroft.stop()


@pytest.mark.timeout(900)
@pytest.mark.parametrize("lang", sorted(ROWS))
def test_golden_rows_match_their_intent(lang):
    rows = ROWS[lang]
    matched = _match_all(lang, rows)
    misses = []
    hits = {row["intent_label"]: 0 for row in rows}
    for row, got in zip(rows, matched):
        if got == f"{SKILL_ID}:{row['intent_label']}":
            hits[row["intent_label"]] += 1
        else:
            misses.append(f"{row['utterance']!r}: expected {row['intent_label']}, got {got}")
    starved = sorted(label for label, count in hits.items()
                     if count < MIN_MATCHED_ROWS_PER_INTENT)
    rate = 1 - len(misses) / len(rows)
    print(f"[{lang}] {rate:.1%} of {len(rows)} rows match", *misses, sep="\n  ")
    if starved:
        print(f"[{lang}] intents below {MIN_MATCHED_ROWS_PER_INTENT} matched rows: {starved}")
    assert not starved, (
        f"[{lang}] intents below {MIN_MATCHED_ROWS_PER_INTENT} matched rows: {starved}"
    )
    if lang in GOLDEN_LOCALE_GAPS:
        measured, reason = GOLDEN_LOCALE_GAPS[lang]
        assert rate >= measured - GAP_TOLERANCE, (
            f"[{lang}] {rate:.1%} of rows match, more than {GAP_TOLERANCE:.0%} "
            f"below the measured {measured:.1%}"
        )
        assert rate < MIN_MATCH_RATE, (
            f"[{lang}] {rate:.1%} of rows match, the gap is closed: remove it "
            f"from GOLDEN_LOCALE_GAPS"
        )
        pytest.xfail(f"[{lang}] {rate:.1%} of rows match: {reason}")
    assert rate >= MIN_MATCH_RATE, (
        f"[{lang}] {rate:.1%} of rows match, below {MIN_MATCH_RATE:.0%}:\n  " + "\n  ".join(misses)
    )


@pytest.mark.timeout(900)
@pytest.mark.parametrize("lang", [
    pytest.param(lang, marks=pytest.mark.xfail(reason=NEGATIVE_ENGINE_GAPS[lang]))
    if lang in NEGATIVE_ENGINE_GAPS else lang
    for lang in sorted(NEGATIVE_ROWS)
])
def test_negative_rows_match_no_skill_intent(lang):
    rows = NEGATIVE_ROWS[lang]
    retrain = NEGATIVE_PUBLISHED_MODEL_CLAIMS.get(lang, {})
    known = {**NEGATIVE_KNOWN_CLAIMS.get(lang, {}), **retrain}
    matched = _match_all(lang, rows)
    claims = [(row["utterance"], got.removeprefix(f"{SKILL_ID}:"))
              for row, got in zip(rows, matched)
              if got and got.startswith(f"{SKILL_ID}:")]
    unknown = [f"{utterance!r}: matched {intent}" for utterance, intent in claims
               if known.get(utterance) != intent]
    print(f"[{lang}] {len(claims)} of {len(rows)} negative rows claimed, "
          f"{len(unknown)} not in NEGATIVE_KNOWN_CLAIMS", *unknown, sep="\n  ")
    assert not unknown, f"[{lang}] negative rows matched this skill:\n  " + "\n  ".join(unknown)
    gone = [f"{utterance!r}: {intent}" for utterance, intent in retrain.items()
            if (utterance, intent) not in claims]
    assert not gone, (f"[{lang}] claims no longer made, remove them from "
                      f"NEGATIVE_PUBLISHED_MODEL_CLAIMS:\n  " + "\n  ".join(gone))


LOCALE_ROOT = END2END_DIR.parents[1] / "locale"


def _intent_names(locale_dir):
    return {path.name for path in locale_dir.rglob("*.intent")}


def test_every_shipping_locale_has_a_golden_file():
    golden = {p.stem.split("_", 2)[2] for p in END2END_DIR.glob("golden_utterances_*.jsonl")}
    shipping = {d.name for d in LOCALE_ROOT.iterdir() if d.is_dir() and any(d.rglob("*.intent"))}
    assert golden == shipping, f"golden files {sorted(golden ^ shipping)} differ from shipping locales"


@pytest.mark.parametrize("lang", sorted(d.name for d in LOCALE_ROOT.iterdir() if d.is_dir()))
def test_every_en_us_intent_file_exists_in_locale(lang):
    missing = _intent_names(LOCALE_ROOT / "en-US") - _intent_names(LOCALE_ROOT / lang)
    assert not missing, f"[{lang}] intent files missing: {sorted(missing)}"
