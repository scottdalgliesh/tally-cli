import os
from pathlib import Path

root = Path.home() / 'AppData/Local/tally'
if not root.exists():
    root.mkdir(parents=True)

# conditionally switch to testing database based on environment variable
if os.environ.get('TALLY_TESTING') == '1':
    DB_URL = root / 'test.db'
else:
    DB_URL = root / 'tally.db'
