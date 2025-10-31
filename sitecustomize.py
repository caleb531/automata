"""Project-wide site customizations for test and dev runs.

This module is imported automatically by Python (via the `site` module) if it
is importable on sys.path. Placing it at the repository root ensures it is
available when running the test suite from the project directory, so filters
apply before third-party packages are imported.

We use it to suppress noisy SyntaxWarning messages emitted by a transitive
dependency (`pydub.utils`) due to non-raw regex strings. These warnings are
benign and clutter test output. To disable this suppression locally, set
`AUTOMATA_WARNINGS_STRICT=1` in your environment.
"""

from __future__ import annotations

import os
import warnings


def _enable_warning_suppression() -> bool:
    # Allow opting out by setting AUTOMATA_WARNINGS_STRICT=1
    return os.environ.get("AUTOMATA_WARNINGS_STRICT", "0") != "1"


if _enable_warning_suppression():
    # Suppress SyntaxWarning originating from pydub.utils. Use append=False so
    # our rule is checked first, even if the test runner adds its own filters.
    warnings.filterwarnings(
        "ignore",
        category=SyntaxWarning,
        module=r"^pydub(\.|$)",
        append=False,
    )

    # As a robust fallback (in case another tool resets filters), monkey-patch
    # warnings.showwarning to drop only the specific noisy warnings while delegating all
    # others unchanged.
    _orig_showwarning = warnings.showwarning

    from typing import Optional, TextIO, Type

    def _showwarning_filter(
        message: Warning,
        category: Type[Warning],
        filename: str,
        lineno: int,
        file: Optional[TextIO] = None,
        line: Optional[str] = None,
    ) -> None:
        try:
            is_pydub_utils = filename.endswith("/pydub/utils.py") or filename.endswith(
                "\\pydub\\utils.py"
            )
            if category is SyntaxWarning and is_pydub_utils:
                return  # swallow this known-noisy warning
        except Exception:
            # On any unexpected error, fall back to original behavior.
            pass
        return _orig_showwarning(
            message,
            category,
            filename,
            lineno,
            file=file,
            line=line,
        )

    warnings.showwarning = _showwarning_filter  # type: ignore[assignment]
