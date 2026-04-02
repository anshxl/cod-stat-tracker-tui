"""Op Kill Tracker — terminal-based operator skill kill counter."""

import json
import sys


def _die(msg: str) -> None:
    """Print error and exit."""
    print(f"Error: {msg}", file=sys.stderr)
    raise SystemExit(msg)


def load_config(path: str) -> dict:
    """Load and validate config.json."""
    try:
        with open(path) as f:
            config = json.load(f)
    except FileNotFoundError:
        _die(f"Config file not found: {path}")
    except json.JSONDecodeError:
        _die(f"Invalid JSON in {path}")

    players = config.get("players", [])
    if len(players) != 5:
        _die(f"'players' must have exactly 5 entries, got {len(players)}")
    if any(not p.strip() for p in players):
        _die("Player names cannot be empty")

    op_defaults = config.get("op_defaults", {})
    for mode in ("HP", "Control"):
        if mode not in op_defaults:
            _die(f"'op_defaults' missing required mode: {mode}")
        if len(op_defaults[mode]) != 5:
            _die(f"'op_defaults.{mode}' must have exactly 5 entries, got {len(op_defaults[mode])}")

    return config
