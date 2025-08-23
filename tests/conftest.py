"""
Pytest configuration for sccpt tests.
"""

import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    
    # Cleanup any test files in /tmp
    for path in Path("/tmp").glob("test-*.jpg"):
        try:
            path.unlink()
        except:
            pass
    
    for path in Path("/tmp").glob("screenshot_*.jpg"):
        try:
            path.unlink()
        except:
            pass


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_wsl_environment(monkeypatch):
    """Mock WSL environment for testing."""
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("os.uname", lambda: type('obj', (), {
        'release': 'test-microsoft-WSL2'
    }))