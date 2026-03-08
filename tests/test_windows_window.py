"""
Windows-specific tests for OCPWidget native window integration.

These tests verify that the WNT_Window is initialised correctly on Windows,
specifically that:
  - WA_NativeWindow is set so Qt allocates a real HWND before winId() is called.
  - The HWND is passed to WNT_Window as a PyCapsule (required by OCP pybind11 — plain
    int and ctypes.c_void_p are both rejected with TypeError).
  - Basic widget and OCC context creation succeeds on the Windows platform.
"""

import sys
import ctypes
import pytest
from unittest.mock import patch

# Skip every test in this module on non-Windows platforms.
pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Windows-only tests"
)

from PySide6.QtCore import Qt  # noqa: E402 (import after skip guard)

from cad_widgets import OCPWidget  # noqa: E402


# ---------------------------------------------------------------------------
# Attribute checks
# ---------------------------------------------------------------------------


def test_wa_native_window_attribute(qapp):
    """WA_NativeWindow must be set so Qt allocates a real HWND."""
    widget = OCPWidget()
    assert widget.testAttribute(Qt.WidgetAttribute.WA_NativeWindow), (
        "WA_NativeWindow not set — winId() may not return a valid HWND"
    )


def test_wa_no_system_background_attribute(qapp):
    """WA_NoSystemBackground must be set to prevent Qt from painting the background."""
    widget = OCPWidget()
    assert widget.testAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)


def test_wa_opaque_paint_event_attribute(qapp):
    """WA_OpaquePaintEvent must be set for flicker-free rendering."""
    widget = OCPWidget()
    assert widget.testAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)


# ---------------------------------------------------------------------------
# WNT_Window ctypes integration
# ---------------------------------------------------------------------------


def test_create_occ_window_passes_pycapsule(qapp):
    """_create_occ_window must pass the HWND as a PyCapsule to WNT_Window.

    OCP's pybind11 binding for WNT_Window(theHandle) requires a capsule object
    (PyCapsule wrapping a void*).  Passing a plain int or ctypes.c_void_p raises
    TypeError: incompatible constructor arguments.
    """
    widget = OCPWidget()
    captured = {}

    # Intercept the WNT_Window constructor call inside the module under test.
    import OCP.WNT as _wnt

    original = _wnt.WNT_Window

    def _spy(handle):
        captured["handle"] = handle
        return original(handle)

    with patch("cad_widgets.widgets.ocp_widget.WNT_Window", side_effect=_spy):
        widget._create_occ_window()

    assert "handle" in captured, "_create_occ_window did not call WNT_Window"

    # PyCapsule_CheckExact is a C macro and not exported from the DLL.
    # The reliable portable check is the type name: CPython exposes capsules
    # as type "PyCapsule" (PyCapsule_Type.tp_name).
    handle_type = type(captured["handle"]).__name__
    assert handle_type == "PyCapsule", (
        f"Expected a PyCapsule but got {handle_type!r}. "
        "WNT_Window requires PyCapsule_New(hwnd, None, None) — "
        "ctypes.c_void_p and plain int are rejected by OCP pybind11."
    )


def test_create_occ_window_sets_view_window(qapp):
    """After _create_occ_window runs, the OCC view must have a window assigned.

    This exercises the real WNT_Window constructor (no mocking) and confirms
    that SetWindow() succeeded — i.e. the line under test actually works end-to-end.
    """
    widget = OCPWidget()
    widget._create_occ_window()
    occ_view = widget.get_view()
    assert occ_view.Window() is not None, (
        "V3d_View.Window() returned None after _create_occ_window — "
        "WNT_Window construction or SetWindow() failed"
    )


def test_full_show_lifecycle_sets_view_window(qapp):
    """The normal show() lifecycle must successfully set the OCC window.

    This is the most realistic test: it triggers showEvent → QTimer → _setup_view
    → _create_occ_window, exactly as production code does.
    """
    widget = OCPWidget()
    widget.show()
    qapp.processEvents()  # let the QTimer.singleShot(0, ...) fire
    qapp.processEvents()  # second pass for the nested singleShot in _setup_view

    occ_view = widget.get_view()
    assert occ_view.Window() is not None, (
        "V3d_View.Window() returned None after full show() lifecycle"
    )
    widget.hide()


def test_window_handle_is_nonzero(qapp):
    """winId() must return a non-zero HWND once WA_NativeWindow is set."""
    widget = OCPWidget()
    widget.show()
    qapp.processEvents()
    handle = int(widget.winId())
    widget.hide()
    assert handle != 0, "winId() returned 0 — Qt did not allocate a native HWND"


# ---------------------------------------------------------------------------
# Basic smoke tests
# ---------------------------------------------------------------------------


def test_widget_creation(qapp):
    """OCPWidget can be created without errors on Windows."""
    widget = OCPWidget()
    assert widget is not None
    assert widget.width() > 0
    assert widget.height() > 0


def test_occ_context_initialised(qapp):
    """OCC AIS context must be initialised on Windows."""
    widget = OCPWidget()
    assert widget.get_context() is not None


def test_occ_view_initialised(qapp):
    """OCC V3d view must be initialised on Windows."""
    widget = OCPWidget()
    assert widget.get_view() is not None


def test_occ_viewer_initialised(qapp):
    """OCC V3d viewer must be initialised on Windows."""
    widget = OCPWidget()
    assert widget.get_viewer() is not None


def test_services_initialised(qapp):
    """SelectionService and ViewService must be available on Windows."""
    widget = OCPWidget()
    assert widget.get_selection_service() is not None
    assert widget.get_view_service() is not None
