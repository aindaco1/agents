#!/usr/bin/env python3
"""Run under the chosen installed Hermes Python, inside the pilot OS guard.

Usage: python -I pilot_hermes_probe.py /absolute/hermes-source
Creates/opens only the synthetic home's actual Hermes SessionDB. No model call,
gateway startup, dependency provisioning, copied user content, or fake path probe.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from hermes_constants import get_hermes_home, get_default_hermes_root, get_config_path, get_skills_dir
from hermes_state import SessionDB

db = SessionDB()
try:
    print(json.dumps({'home': str(get_hermes_home()), 'root': str(get_default_hermes_root()),
                      'config': str(get_config_path()), 'skills': str(get_skills_dir()),
                      'state_db': str(Path(db.db_path).resolve())}))
finally:
    db.close()
