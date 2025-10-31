"""Test helpers for optional dependencies.

Provides a VISUAL_OK flag indicating whether visualization extras are
importable (pygraphviz, coloraide). Use in tests to conditionally skip
diagram-related tests on environments lacking these extras.
"""

from __future__ import annotations

# Shared skip reason for tests that require visualization extras
VISUAL_SKIP_REASON = "visual extras (pygraphviz, coloraide) not available"

PYGRAPHVIZ_OK = False
COLORAIDE_OK = False

try:  # Try importing pygraphviz, catching linkage errors too
    import pygraphviz as pgv  # type: ignore  # noqa: F401

    # Access an attribute to ensure the extension module is importable/linked
    _ = getattr(pgv, "AGraph", None)
    PYGRAPHVIZ_OK = True
except Exception:
    PYGRAPHVIZ_OK = False

try:
    import coloraide  # type: ignore  # noqa: F401

    COLORAIDE_OK = True
except Exception:
    COLORAIDE_OK = False

VISUAL_OK: bool = PYGRAPHVIZ_OK and COLORAIDE_OK
