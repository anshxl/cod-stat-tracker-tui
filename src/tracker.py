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
    raise SystemExit(1)


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
        if any(not op.strip() for op in op_defaults[mode]):
            _die(f"Op names in '{mode}' cannot be empty")

    return config


class TrackerState:
    """Manages kill counts, pull counts, and undo stack."""

    def __init__(self, num_players: int, player_names: list[str] | None = None):
        self.kills = [0] * num_players
        self.pulls = [0] * num_players
        self.undo_stack: list[tuple[int, str]] = []
        self.last_action = ""
        self._names = player_names or [f"Player {i+1}" for i in range(num_players)]

    def increment(self, player_idx: int) -> None:
        self.kills[player_idx] += 1
        self.undo_stack.append((player_idx, "kill"))
        name = self._names[player_idx]
        self.last_action = f"+1 kill {name} (total: {self.kills[player_idx]})"

    def record_pull(self, player_idx: int) -> None:
        self.pulls[player_idx] += 1
        self.undo_stack.append((player_idx, "pull"))
        name = self._names[player_idx]
        self.last_action = f"+1 pull {name} (total: {self.pulls[player_idx]})"

    def undo(self) -> None:
        if not self.undo_stack:
            self.last_action = "Nothing to undo"
            return
        player_idx, action = self.undo_stack.pop()
        name = self._names[player_idx]
        if action == "kill":
            self.kills[player_idx] = max(0, self.kills[player_idx] - 1)
            self.last_action = f"Undo kill {name} (total: {self.kills[player_idx]})"
        else:
            self.pulls[player_idx] = max(0, self.pulls[player_idx] - 1)
            self.last_action = f"Undo pull {name} (total: {self.pulls[player_idx]})"


HEADER = ["date", "opponent", "map", "mode", "player", "operator", "op_kills", "op_pulls"]


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
                session["pulls"][i],
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


def draw_screen(stdscr, session: dict, state: TrackerState) -> None:
    """Render the tracking UI."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Header
    header = f"Op Kill Tracker | vs {session['opponent']} | {session['map']} | {session['mode']}"
    stdscr.addstr(0, 0, header[:w-1], curses.A_BOLD)
    stdscr.addstr(1, 0, "\u2500" * min(len(header), w-1))

    # Player rows
    for i in range(5):
        name = session["players"][i]
        op = session["operators"][i]
        kills = state.kills[i]
        pulls = state.pulls[i]
        bar = "\u2588" * kills
        line = f"[{i+1}] {name:<14} | {op:<16} | {bar} {kills}k / {pulls}p"
        row = i + 3
        if row < h - 3:
            stdscr.addstr(row, 0, line[:w-1])

    # Separator
    sep_row = 9
    if sep_row < h - 2:
        stdscr.addstr(sep_row, 0, "\u2500" * min(50, w-1))

    # Last action
    if sep_row + 1 < h - 1:
        action = state.last_action or "Ready"
        stdscr.addstr(sep_row + 1, 0, f"Last action: {action}"[:w-1])

    # Legend
    if sep_row + 2 < h:
        stdscr.addstr(sep_row + 2, 0, "[1-5] Kill  [q/w/e/r/t] Pull  [z] Undo  [x] End"[:w-1])

    stdscr.refresh()


def run_tracker(stdscr, session: dict) -> tuple[list[int], list[int]]:
    """Run the curses tracking loop. Returns (kills, pulls)."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.timeout(100)

    state = TrackerState(5, player_names=session["players"])

    KILL_MAP = {
        ord("1"): 0, ord("2"): 1, ord("3"): 2, ord("4"): 3, ord("5"): 4,
    }
    PULL_MAP = {
        ord("q"): 0, ord("w"): 1, ord("e"): 2, ord("r"): 3, ord("t"): 4,
    }

    while True:
        draw_screen(stdscr, session, state)
        key = stdscr.getch()

        if key in KILL_MAP:
            state.increment(KILL_MAP[key])
        elif key in PULL_MAP:
            state.record_pull(PULL_MAP[key])
        elif key == ord("z"):
            state.undo()
        elif key in (ord("x"), 27):  # x or Esc
            # Confirmation prompt
            h, _ = stdscr.getmaxyx()
            stdscr.addstr(h - 1, 0, "End session and save? (y/n) ", curses.A_BOLD)
            stdscr.refresh()
            stdscr.nodelay(False)
            stdscr.timeout(-1)
            confirm = stdscr.getch()
            stdscr.timeout(100)
            if confirm in (ord("y"), ord("Y")):
                return state.kills, state.pulls
            else:
                state.last_action = "Cancelled — continuing"

    return state.kills, state.pulls


def main() -> None:
    """Entry point: load config, collect metadata, run tracker, save CSV."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "op_kills.csv")

    config = load_config(config_path)
    session = get_session_metadata(config)

    kills, pulls = curses.wrapper(run_tracker, session)

    session["date"] = date.today().isoformat()
    session["kills"] = kills
    session["pulls"] = pulls
    write_csv(csv_path, session)
    print(f"\nSession saved to {csv_path}")
    print("Results:")
    for i in range(5):
        print(f"  {session['players'][i]}: {kills[i]} kills / {pulls[i]} pulls ({session['operators'][i]})")


if __name__ == "__main__":
    main()
