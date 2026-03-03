"""
Pytest configuration and shared fixtures for cad_widgets tests.
"""

import sys
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """
    Create a QApplication instance for tests.
    
    This fixture is session-scoped to ensure only one QApplication
    instance is created for all tests, as QApplication is a singleton.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Note: QApplication cleanup is handled automatically by Qt
