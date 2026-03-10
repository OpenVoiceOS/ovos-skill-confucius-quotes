
# FAQ - Confucius Quotes Skill

## 🌟 General Questions

### What does this skill do?
It provides quotes and biographical facts about the philosopher Confucius. You can ask for a quote or learn about his life.

### Does it work on devices with screens?
**Yes!** If your device has a GUI (like a smart screen), it will show a portrait of Confucius along with the text of the quote or biographical fact.

### Which languages are supported?
The skill is fully localized and supports:
- English (`en-us`)
- Portuguese (`pt-pt`)
- German (`de-de`)
- Danish (`da`)
- Spanish (`es-es`)
- Basque (`eu`)
- Catalan (`ca-es`)
- French (`fr-fr`)

### Is there a cost?
**No.** This is a free and open-source skill, part of the OpenVoiceOS ecosystem.

---

## 🛠️ Technical Questions

### How is this package built?
This package uses `pyproject.toml` with `setuptools` as the build backend. It supports dynamic versioning by reading from `version.py`.

### Where is the version defined?
The source of truth for the version is in `version.py` within the `START_VERSION_BLOCK` markers.

### Which CI/CD workflows are used?
This repository uses the latest `gh-automations@dev` workflows, including:
- `release_workflow.yml`: Alpha releases on PR merge
- `publish_stable.yml`: Stable releases on push to master
- `build_tests.yml`: Build/install verification across Python 3.10-3.12
- `coverage.yml`: Automated test coverage (min 80%)
- `skill_check.yml`: Locale and `skill.json` validation
- `release_preview.yml`: Version bump prediction on PRs
- `repo_health.yml`: Required files and contributor welcome
- `license_tests.yml`: Dependency license auditing
- `pip_audit.yml`: Security vulnerability scanning
- `python_support.yml`: Python compatibility matrix + OPM detection
- `downstream_check.yml`: Downstream dependency verification
- `sync_translations.yml`: Automated translation synchronization
- `conventional-label.yml`: Auto-labels PRs from title prefix

### How do I run tests locally?
You can run tests using `pytest`:
```bash
uv run pytest test/
```
For coverage reporting:
```bash
uv run pytest --cov=ovos_skill_confucius_quotes test/
```

### How are the end-to-end tests structured?

18 tests across 4 test classes:
- **TestConfuciusAdaptEN** (7 tests): All 4 Adapt intents in en-US with alternative phrasings
- **TestConfuciusPadatiousEN** (2 tests): Padatious `who.intent` in en-US
- **TestConfuciusMultilingual** (6 tests): Adapt + Padatious in pt-PT, de-DE, es-ES using `secondary_langs`
- **TestConfuciusFixtures** (3 tests): Replay from recorded JSON fixtures

### How do the multilingual tests work?

MiniCroft's `secondary_langs` parameter patches `Configuration()["secondary_langs"]` before Adapt/Padatious initialize, so they register vocab engines for all specified languages. Without this, only the system's default language has vocab registered.

### How do I regenerate the JSON fixtures?

```bash
python test/end2end/generate_fixtures.py
```

This records live message sequences and saves them as anonymized JSON. Fixtures validate message types and routing but skip data/context checks due to non-deterministic dialog rendering and session timestamps.

### Why is `require_adapt: true` set in `ovoscope.yml`?

The skill tests Adapt intents (ConfuciusQuote, ConfuciusLive, ConfuciusBirth, ConfuciusDeath). Setting `require_adapt: true` makes CI fail explicitly if `ovos-adapt-pipeline-plugin` is missing from `[test]` deps, rather than silently skipping those tests and passing with reduced coverage.

### Why does the skill use `speak()` with manual `meta` instead of `speak_dialog()`?

The skill needs the rendered dialog text for the GUI caption (`show_confucius(utterance)`) before speaking it. Using `speak_dialog()` would render internally and not expose the text for the GUI. Instead, it renders manually via `dialog_renderer.render()`, shows the GUI, then calls `speak()` with explicit `meta={"dialog": ..., "data": {}, "skill": ...}` to preserve dialog traceability.
