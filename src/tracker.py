"""Op Kill Tracker — terminal-based operator skill kill counter."""

import csv
import json
import os
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


class TrackerState:
    """Manages kill counts and undo stack."""

    def __init__(self, num_players: int, player_names: list[str] | None = None):
        self.kills = [0] * num_players
        self.undo_stack: list[int] = []
        self.last_action = ""
        self._names = player_names or [f"Player {i+1}" for i in range(num_players)]

    def increment(self, player_idx: int) -> None:
        self.kills[player_idx] += 1
        self.undo_stack.append(player_idx)
        name = self._names[player_idx]
        self.last_action = f"+1 {name} (total: {self.kills[player_idx]})"

    def undo(self) -> None:
        if not self.undo_stack:
            self.last_action = "Nothing to undo"
            return
        player_idx = self.undo_stack.pop()
        self.kills[player_idx] = max(0, self.kills[player_idx] - 1)
        name = self._names[player_idx]
        self.last_action = f"Undo {name} (total: {self.kills[player_idx]})"


HEADER = ["date", "opponent", "map", "mode", "player", "operator", "op_kills"]


def write_csv(path: str, session: dict) -> None:
    """Append session results to CSV. Creates file with header if it doesn't exist."""
    file_exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(HEADER)
        for i in range(5):
            writer.writerow([
                session["date"],
                session["opponent"],
                session["map"],
                session["mode"],
                session["players"][i],
                session["operators"][i],
                session["kills"][i],
            ])
