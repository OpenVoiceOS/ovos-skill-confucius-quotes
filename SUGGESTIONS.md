
# Enhancement Proposals — ovos-skill-confucius-quotes

## 1. Add Dialog Validation During Skill Load

**Problem**: If locale files are corrupted or missing, the skill loads but fails at runtime when handlers try to render dialogs.

**Proposed Solution**: Add an `initialize()` method (called during skill load) that validates all required dialog keys and issues a warning if any are missing.

```python
def initialize(self) -> None:
    """Validate dialog files are present and readable."""
    required_dialogs = ["quote", "birth", "death", "live", "confucius"]
    for dialog in required_dialogs:
        try:
            # Attempt to render empty template to check file exists
            self.dialog_renderer.render(dialog, {})
        except Exception as e:
            self.log.warning(f"Dialog '{dialog}' missing or malformed: {e}")
```

**Impact**: Medium (improves error visibility, no behavior change for healthy installs)
**Effort**: ~30 minutes
**Priority**: Medium (would improve debugging for translation issues)

---

## 2. Add Adaptive Quote Selection

**Problem**: All handlers speak random quotes, but there's no way for users to request a "specific type" of quote (e.g., philosophical vs. practical).

**Proposed Solution**: Extend `handle_quote()` to detect context from the utterance and filter quotes accordingly. For example, "Tell me a philosophical quote" could search a metadata field in the quote source.

**Impact**: Medium (user-facing feature, requires quote categorization)
**Effort**: ~2-3 hours (depends on quote source availability)
**Priority**: Low (nice-to-have, out of scope for current release)

---

## 3. Add GUI Availability Guard

**Problem**: Skill calls `self.gui.show_image()` unconditionally, but GUI may not be available on headless systems.

**Proposed Solution**: Check GUI availability before calling GUI methods:

```python
def show_confucius(self, caption: str) -> None:
    """Display Confucius image if GUI is available."""
    if self.config_core.get("gui.active", False):
        img = os.path.join(self.root_dir, "gui", "all", "confucius.jpg")
        self.gui.show_image(...)
    # Always speak the caption (GUI optional)
```

**Impact**: Low (improves UX on headless systems, no breaking changes)
**Effort**: ~15 minutes
**Priority**: Medium (quality-of-life for headless deployments)

---

## 4. Internationalize Spoken Text Metadata

**Problem**: Dialog metadata keys (e.g., `"dialog": dialog`) are always in English, even when skill runs in non-English locale.

**Proposed Solution**: Localize metadata by checking `self.lang` and mapping to locale-specific keys.

**Impact**: Low (internal logging only, no user impact)
**Effort**: ~45 minutes
**Priority**: Low (nice-to-have, doesn't affect functionality)

---

## 5. Add Padatious Intent Support

**Problem**: Skill only uses Adapt `IntentBuilder` patterns, missing Padatious (fuzzy) intent support.

**Proposed Solution**: Add alternate intents using Padatious `.intent` files for improved matching on variant phrasings.

**Impact**: Medium (improves intent recognition accuracy)
**Effort**: ~1-2 hours (requires Padatious training data)
**Priority**: Medium (would reduce false negatives)

---

## Summary Table

| # | Title | Impact | Effort | Priority | Blocker |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Dialog Validation | Medium | 30 min | Medium | No |
| 2 | Adaptive Quotes | Medium | 2-3h | Low | No |
| 3 | GUI Guard | Low | 15 min | Medium | No |
| 4 | Localize Metadata | Low | 45 min | Low | No |
| 5 | Padatious Intents | Medium | 1-2h | Medium | No |

**Recommended Next Step**: Implement #1 (validation) for robustness, then #3 (GUI guard) for headless support.
