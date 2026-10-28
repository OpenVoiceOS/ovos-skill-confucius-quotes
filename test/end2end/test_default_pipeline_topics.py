"""On the default pipeline "what did Confucius say about life" reaches the quote.

The golden test runs only the m2v prototype engine. The default pipeline puts
padatious and adapt ahead of the published m2v model, and a question about a
topic must reach confucius_quote there and not who or confucius_lifespan.
"""
import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-confucius-quotes.openvoiceos"
PIPELINE = ["ovos-padatious-pipeline-plugin-high", "ovos-adapt-pipeline-plugin-high",
            "ovos-m2v-pipeline-high", "ovos-padatious-pipeline-plugin-medium",
            "ovos-adapt-pipeline-plugin-medium", "ovos-m2v-pipeline-medium"]
TOPIC_QUESTIONS = {
    "da-DK": ["hvad sagde confucius om livet", "hvad siger confucius om livet"],
    "fa-IR": ["کنفوسیوس درباره زندگی چه گفته است"],
    "fr-FR": ["qu'a dit confucius sur la sagesse", "que disait confucius sur la sagesse"],
    "gl-ES": ["que dixo confucio sobre a vida"],
    "nl-NL": ["wat zei confucius over het leven"],
    "ru-RU": ["что говорил конфуций о жизни", "что сказал конфуций о жизни"],
    "sv-SE": ["vad sa konfucius om livet"],
}


@pytest.mark.timeout(900)
@pytest.mark.parametrize("lang", sorted(TOPIC_QUESTIONS))
def test_a_question_about_a_topic_reaches_the_quote(lang):
    minicroft = get_minicroft([SKILL_ID], default_pipeline=PIPELINE, lang=lang, max_wait=300)
    try:
        reached = {}
        for utterance in TOPIC_QUESTIONS[lang]:
            session = Session(f"topic-{lang}-{abs(hash(utterance))}")
            session.lang = lang
            session.pipeline = PIPELINE
            capture = CaptureSession(minicroft)
            capture.capture(Message("recognizer_loop:utterance",
                                    {"utterances": [utterance], "lang": lang},
                                    {"session": session.serialize()}), timeout=20)
            reached[utterance] = [m.msg_type.split(":", 1)[1] for m in capture.finish()
                                  if m.msg_type.startswith(SKILL_ID + ":")]
        assert reached == {u: ["confucius_quote"] for u in TOPIC_QUESTIONS[lang]}
    finally:
        minicroft.stop()
