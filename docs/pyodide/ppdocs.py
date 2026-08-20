"""Helpers for live PhreeqPython examples in the docs."""

from __future__ import annotations

import base64
import builtins
import io


def show_plot(fig):
    """Render a matplotlib figure below the Pyodide editor."""
    from js import document, window

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    fig.clf()

    root = getattr(window, "__ppdocsPyodideRoot", None) or document.querySelector(".pyodide")
    plots = root.querySelectorAll("img.pyodide-plot")
    for i in range(plots.length):
        plots.item(i).remove()

    img = document.createElement("img")
    img.className = "pyodide-plot"
    img.src = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    img.style.maxWidth = "100%"
    root.appendChild(img)


def load_tsv(name):
    """Load a TSV from ``docs/examples/gas_data`` (path relative to the Examples tab)."""
    import pandas as pd
    from js import window
    from pyodide.http import open_url

    path = window.location.pathname.rstrip("/")
    if path.endswith(".html"):
        path = path.rsplit("/", 1)[0]
    examples_root = path.rsplit("/", 1)[0]
    url = window.location.origin + examples_root + "/gas_data/" + name
    return pd.read_csv(open_url(url), sep="\t", index_col=0)


def prepare():
    """Import names used by every live example."""
    from phreeqpython import PhreeqPython

    builtins.show_plot = show_plot
    builtins.load_tsv = load_tsv
    builtins.PhreeqPython = PhreeqPython
    try:
        import numpy as np
        builtins.np = np
    except ImportError:
        pass
    try:
        import matplotlib.pyplot as plt
        builtins.plt = plt
    except ImportError:
        pass
