"""
Root forwarder proxy for freightrates/bdi_live_scraper.py.
Guarantees a single source of truth and prevents root/subdirectory divergence.
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CANONICAL_SCRIPT = os.path.join(SCRIPT_DIR, 'freightrates', 'bdi_live_scraper.py')

if __name__ == '__main__':
    cmd = [sys.executable, CANONICAL_SCRIPT] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
