"""Op Kill Tracker — terminal-based operator skill kill counter."""

import csv
import curses
import json
import os
import sys
from datetime import date


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


def get_session_metadata(config: dict) -> dict:
    """Collect session metadata via terminal prompts. Returns session dict."""
    # Opponent
    while True:
        opponent = input("Opponent team name: ").strip()
        if opponent:
            break
        print("Opponent name cannot be empty.")

    # Map
    while True:
        map_name = input("Map name: ").strip()
        if map_name:
            break
        print("Map name cannot be empty.")

    # Mode
    while True:
        mode = input("Mode (HP/Control): ").strip().upper()
        if mode in ("HP", "CONTROL"):
            if mode == "CONTROL":
                mode = "Control"
            break
        print("Invalid mode. Enter HP or Control.")

    # Op assignments
    players = config["players"]
    operators = list(config["op_defaults"][mode])

    print(f"\nDefault Op loadout for {mode}:")
    for i, (player, op) in enumerate(zip(players, operators)):
        print(f"  [{i+1}] {player}: {op}")

    confirm = input("\nConfirm defaults? (y/n): ").strip().lower()
    if confirm != "y":
        for i, (player, op) in enumerate(zip(players, operators)):
            override = input(f"  {player} [{op}]: ").strip()
            if override:
                operators[i] = override

    return {
        "opponent": opponent,
        "map": map_name,
        "mode": mode,
        "players": players,
        "operators": operators,
    }
