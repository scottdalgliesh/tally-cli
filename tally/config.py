# The db url is provided below to facilitate patching during unit tests.
# Without providing this in a seperate module, patching must be completed
# seperately for each file, due to evaluation at import (vs at execution).

from pathlib import Path

root = Path.home() / 'AppData/Local/tally'
if not root.exists():
    root.mkdir(parents=True)

DB_URL = root / 'tally.db'
