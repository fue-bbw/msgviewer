import pytest

pytest.importorskip("tkinter", exc_type=ImportError)

from msgviewer.gui import MsgViewerApp, main  # noqa: E402


def test_app_builds():
    import tkinter as tk

    try:
        app = MsgViewerApp()
    except tk.TclError:
        pytest.skip("kein Display verfügbar")
    assert app.format_var.get() == "eml"
    assert app.summary is None
    app.root.destroy()


def test_main_requires_display():
    import tkinter as tk

    try:
        tk.Tk().destroy()
    except tk.TclError:
        pytest.skip("kein Display verfügbar")
