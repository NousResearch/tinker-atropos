from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path('/Users/heomin/.hermes/scripts')
SCRIPT_PATH = SCRIPT_DIR / 'paperclip-external-standard-check.py'



def load_module():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location('paperclip_external_standard_check', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def test_detect_auth_scope_allows_local_trusted_without_api_key(monkeypatch):
    module = load_module()
    monkeypatch.delenv('PAPERCLIP_API_KEY', raising=False)
    monkeypatch.setattr(module, 'fetch_public_health', lambda api_base: {'deploymentMode': 'local_trusted'})

    scope = module.detect_auth_scope()

    assert scope['kind'] == 'local_implicit_board'
    assert scope['deployment_mode'] == 'local_trusted'



def test_detect_auth_scope_reports_missing_api_key_when_public_health_not_local_trusted(monkeypatch):
    module = load_module()
    monkeypatch.delenv('PAPERCLIP_API_KEY', raising=False)
    monkeypatch.setattr(module, 'fetch_public_health', lambda api_base: {'deploymentMode': 'private'})

    scope = module.detect_auth_scope()

    assert scope['kind'] == 'none'
    assert scope['reason'] == 'missing_api_key'
