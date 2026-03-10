Last Edit: Claude Sonnet 4.6 - 2026-03-10 - Motive: End-to-end test improvements and multilingual testing.

# Maintenance Report - ovos-skill-confucius-quotes

## 2026-03-10 - End-to-End Test Improvements
- **AI Model**: Claude Sonnet 4.6
- **Actions Taken**:
    - Rewrote `test/end2end/test_confucius.py`: 4 → 18 tests (9 EN + 6 multilingual + 3 fixture)
    - Added missing `ConfuciusLive` intent test and alternative utterance phrasings
    - Added multilingual tests (pt-PT, de-DE, es-ES) using ovoscope `secondary_langs`
    - Added JSON fixture recording (`generate_fixtures.py`) and replay tests (Pattern 4)
    - Refactored `__init__.py`: extracted `_speak_and_show()` helper, added `meta` with `dialog` key to `speak()` calls for dialog traceability
    - Fixed ovoscope bugs: `from_message` crashed with `async_messages=None`, `from_message` didn't filter GUI messages, `from_message` didn't pass `ignore_messages`/`eof_msgs` to returned test
    - Extended ovoscope: added `lang` and `secondary_langs` params to `MiniCroft` for multilingual vocab registration, added `ignore_gui` param to `from_message`
- **Oversight**: All 18 e2e tests + 5 unit tests pass. Multilingual tests validate Adapt + Padatious in 3 non-English languages.

## 2026-03-09 - Full CI Modernization
- **AI Model**: Claude Sonnet 4.6
- **Actions Taken**:
    - Renamed `license_check.yml` → `license_tests.yml` (standard naming)
    - Added `if:` merged/dispatch guard to `release_workflow.yml`
    - Added `notify_matrix: true` to `release_workflow.yml` and `publish_stable.yml`
    - Fixed `conventional-label.yml` version pin (`@v1.2.1` → `@v1`)
    - Fixed `release_preview.yml` branches (`[dev, master]` → `[dev]`)
    - Added `repo_health.yml` — required files check + first-time contributor greeting
    - Committed pending `__init__.py` image path fix
    - Updated FAQ.md (added fr-fr to languages, full workflow list)
- **Oversight**: Tests verified passing (5/5). All 13 workflows now canonical.

## 2026-03-09 - Enhanced CI Checks
- **AI Model**: Gemini CLI
- **Actions Taken**:
    - Added `.github/workflows/pip_audit.yml` to include security auditing in PR comments.
    - Added `.github/workflows/python_support.yml` to provide a compatibility matrix (Python 3.8-3.12) and verify `ovos-plugin-manager` detection in regular and editable modes.
    - Updated `.github/workflows/release_preview.yml` to include `package_name` for release channel compatibility reporting.
- **Oversight**: Verified compatibility with updated `gh-automations@dev` workflows.

## 2026-03-09 - Workflow and Packaging Update
- **AI Model**: Gemini CLI
- **Actions Taken**:
    - Updated `.github/workflows/release_workflow.yml` to use `OpenVoiceOS/gh-automations/.github/workflows/publish-alpha.yml@dev`.
    - Updated `.github/workflows/publish_stable.yml` to use `OpenVoiceOS/gh-automations/.github/workflows/publish-stable.yml@dev`.
    - Created `.github/workflows/skill_check.yml` using `OpenVoiceOS/gh-automations/.github/workflows/skill-check.yml@dev`.
    - Created `.github/workflows/release_preview.yml` using `OpenVoiceOS/gh-automations/.github/workflows/release-preview.yml@dev`.
    - Created `.github/workflows/license_check.yml` using `OpenVoiceOS/gh-automations/.github/workflows/license-check.yml@dev`.
    - Created `.github/workflows/sync_translations.yml` using `OpenVoiceOS/gh-automations/.github/workflows/sync-translations.yml@dev`.
    - Created `.github/workflows/coverage.yml` using `OpenVoiceOS/gh-automations/.github/workflows/coverage.yml@dev`.
    - Removed legacy `.github/workflows/sync_tx.yml` and `.github/workflows/unit_tests.yml`.
    - Migrated packaging from `setup.py` to `pyproject.toml` with `setuptools` build-backend.
    - Updated `version.py` to include `__version__` string for dynamic versioning.
    - Removed `setup.py` and `MANIFEST.in`.
- **Oversight**: Verified file structure and workflow references against `gh-automations` documentation and `AGENTS.md`.

## Transparency Report
- **AI Model**: Gemini CLI (v1)
- **Actions Taken**: Automated migration of packaging and CI/CD configuration to meet the latest OpenVoiceOS standards.
- **Oversight**: The agent followed the `AGENTS.md` and `gh-automations` guidelines. Manual verification of the resulting YAML and TOML syntax was performed.
