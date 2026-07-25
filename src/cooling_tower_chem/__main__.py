"""Module entry point, so the CLI can be run as ``python -m cooling_tower_chem``.

The ``ctchem`` console script is the usual way in, but it depends on the
install's script directory being on ``PATH``. That is not always true --
notably inside conda test environments on Windows, and in any virtualenv the
caller has not activated. Running the module works regardless.
"""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
