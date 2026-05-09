"""Tests for the v0.3 gated reveal protocol — Identity.export_nsec
and Identity.export_seed_phrase.

Each test sets / unsets NOSTRKEY_REVEAL_CODE and points
NOSTRKEY_AUDIT_LOG at a tmp file so tests don't pollute ~/.nostrkey/.
"""

import os
import tempfile
from pathlib import Path

import pytest

from nostrkey.identity import Identity


_VALID_PURPOSE = "paper backup before deploying agent to production"


def _set_env(monkeypatch, code: str | None, log_path: Path):
    if code is None:
        monkeypatch.delenv("NOSTRKEY_REVEAL_CODE", raising=False)
    else:
        monkeypatch.setenv("NOSTRKEY_REVEAL_CODE", code)
    monkeypatch.setenv("NOSTRKEY_AUDIT_LOG", str(log_path))


def _audit_lines(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return log_path.read_text().splitlines()


# ---------- export_nsec ----------


def test_export_nsec_succeeds_with_valid_code_and_purpose(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot = Identity.generate()
    nsec = bot.export_nsec(confirmation_code="good-code", purpose=_VALID_PURPOSE)
    assert nsec.startswith("nsec1")
    assert nsec == bot.nsec
    lines = _audit_lines(log)
    assert any("export_nsec\tok" in line for line in lines)


def test_export_nsec_refuses_when_env_not_set(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, None, log)
    bot = Identity.generate()
    with pytest.raises(PermissionError, match="env var is not set"):
        bot.export_nsec(confirmation_code="anything", purpose=_VALID_PURPOSE)
    lines = _audit_lines(log)
    assert any("export_nsec\tcode_mismatch_or_missing" in line for line in lines)


def test_export_nsec_refuses_on_code_mismatch(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "expected-code", log)
    bot = Identity.generate()
    with pytest.raises(PermissionError, match="does not match"):
        bot.export_nsec(confirmation_code="wrong-code", purpose=_VALID_PURPOSE)
    lines = _audit_lines(log)
    assert any("export_nsec\tcode_mismatch_or_missing" in line for line in lines)


def test_export_nsec_refuses_on_short_purpose(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot = Identity.generate()
    with pytest.raises(PermissionError, match="at least 20 characters"):
        bot.export_nsec(confirmation_code="good-code", purpose="too short")
    lines = _audit_lines(log)
    assert any("export_nsec\tpurpose_too_short" in line for line in lines)


def test_export_nsec_refuses_empty_code(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot = Identity.generate()
    with pytest.raises(PermissionError, match="non-empty string"):
        bot.export_nsec(confirmation_code="", purpose=_VALID_PURPOSE)


# ---------- export_seed_phrase ----------


def test_export_seed_phrase_succeeds_with_valid_inputs(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot, original_phrase = Identity.generate_with_seed()
    phrase = bot.export_seed_phrase(confirmation_code="good-code", purpose=_VALID_PURPOSE)
    assert phrase == original_phrase
    assert len(phrase.split()) == 12
    lines = _audit_lines(log)
    assert any("export_seed_phrase\tok" in line for line in lines)


def test_export_seed_phrase_raises_when_no_phrase_held(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot = Identity.generate()  # no seed phrase
    with pytest.raises(LookupError, match="No seed phrase"):
        bot.export_seed_phrase(confirmation_code="good-code", purpose=_VALID_PURPOSE)


def test_export_seed_phrase_refuses_on_code_mismatch(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "expected-code", log)
    bot, _phrase = Identity.generate_with_seed()
    with pytest.raises(PermissionError, match="does not match"):
        bot.export_seed_phrase(confirmation_code="wrong-code", purpose=_VALID_PURPOSE)


def test_export_seed_phrase_refuses_on_short_purpose(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot, _phrase = Identity.generate_with_seed()
    with pytest.raises(PermissionError, match="at least 20 characters"):
        bot.export_seed_phrase(confirmation_code="good-code", purpose="paper backup")


def test_seed_phrase_wiped_on_wipe(monkeypatch, tmp_path):
    log = tmp_path / "audit.log"
    _set_env(monkeypatch, "good-code", log)
    bot, _phrase = Identity.generate_with_seed()
    bot.wipe()
    with pytest.raises(LookupError):
        bot.export_seed_phrase(confirmation_code="good-code", purpose=_VALID_PURPOSE)


# ---------- backwards compatibility ----------


def test_direct_nsec_access_still_works():
    """v0.3 must not break .nsec / .npub direct access."""
    bot = Identity.generate()
    assert bot.npub.startswith("npub1")
    assert bot.nsec.startswith("nsec1")


def test_backup_card_still_returns_nsec():
    """v0.3 must not break backup_card() — backwards compat."""
    bot = Identity.generate()
    card = bot.backup_card()
    assert "npub" in card
    assert "nsec" in card
    assert card["nsec"].startswith("nsec1")
