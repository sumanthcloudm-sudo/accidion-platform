#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).resolve().parents[2]
required = ['README.md', 'RULES.md', 'SECURITY.md', 'CONTRIBUTING.md', 'docs/ARCHITECTURE.md', 'services', 'connectors', 'infra', 'tests', 'operations', 'compliance']
missing = [p for p in required if not (root / p).exists()]
if missing:
    raise SystemExit('Missing required paths: ' + ', '.join(missing))
print('Repository scaffold check passed.')
