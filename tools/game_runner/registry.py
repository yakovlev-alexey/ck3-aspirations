"""Names shared by CLI, runner, MCP and repository contract checks."""
import json
from pathlib import Path

SCENARIOS = tuple(json.loads(Path(__file__).with_name('scenarios.json').read_text(encoding='utf-8-sig')))
if not SCENARIOS or len(set(SCENARIOS)) != len(SCENARIOS) or any(not isinstance(name, str) for name in SCENARIOS):
    raise ValueError('Invalid registered scenario names')
