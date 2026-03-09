# ❓ FAQ - Confucius Quotes Skill

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
- `release_workflow.yml`: Alpha releases on PR merge.
- `publish_stable.yml`: Stable releases on push to master.
- `skill_check.yml`: Locale and `skill.json` validation.
- `coverage.yml`: Automated test coverage reporting.
- `license_check.yml`: Dependency license auditing.
- `sync_translations.yml`: Automated translation synchronization.

### How do I run tests locally?
You can run tests using `pytest`:
```bash
uv run pytest test/
```
For coverage reporting:
```bash
uv run pytest --cov=ovos_skill_confucius_quotes test/
```
