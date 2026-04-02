# Op Kill Tracker — CLAUDE.md

## Purpose

A terminal-based keystroke counter for manually tracking Operator Skill kills during Call of Duty scrim VOD review. The tool runs in a focused terminal window alongside a VOD player (split-screen on macOS). The operator presses number keys (1-5) to increment kill counters for the corresponding player whenever they observe an Op kill in the VOD.

This tool exists because the game provides no API or mechanism to track Operator Skill kills per player. Previous manual tracking was too tedious, especially when multiple players use Ops simultaneously.

## Tech Stack

- Python 3.11
- `uv` for package management
- Terminal UI via `curses` (stdlib — no external dependency needed)
- macOS (Sequoia 26.3) — focused-window keypress capture only, no global hotkeys

## Configuration

A `config.json` file in the project root stores the roster and per-mode default Op assignments.

### config.json schema

```json
{
  "players": ["PlayerName1", "PlayerName2", "PlayerName3", "PlayerName4", "PlayerName5"],
  "op_defaults": {
    "HP": ["OpName", "OpName", "OpName", "OpName", "OpName"],
    "Control": ["OpName", "OpName", "OpName", "OpName", "OpName"]
  }
}
```

- `players`: Array of 5 strings. Index corresponds to key mapping (index 0 = key 1, index 1 = key 2, etc.). Fixed for a season; edited directly in the file when roster changes.
- `op_defaults`: Keyed by mode. Each value is an array of 5 Op names, positionally matched to `players`. These are loaded as defaults during session startup and can be overridden per-session.

The tool should validate on startup:
- File exists and is valid JSON
- `players` has exactly 5 entries, no empty strings
- `op_defaults` has entries for both `HP` and `Control`
- Each Op array has exactly 5 entries

If validation fails, print a clear error message explaining what's wrong and exit.

## Session Startup Flow

Sequential prompts in the terminal before tracking begins:

1. **Opponent team name**: Free text input. Required, cannot be empty.
2. **Map name**: Free text input. Required, cannot be empty.
3. **Mode**: Selection from `HP` or `Control`. Only these two modes use Ops (SnD does not). Validate input.
4. **Op assignments**: Display the default Op loadout for the selected mode from config. For each player, show `PlayerName: DefaultOp`. Prompt the user to confirm all defaults or override individual assignments.
   - Suggested UX: Show the full loadout, ask "Confirm? (y/n)". If `y`, proceed. If `n`, prompt per-player for a replacement Op name (pressing Enter keeps the default for that player).

After all metadata is collected, transition to the active tracking UI.

## Active Tracking Phase

### Display

A persistent terminal UI (curses) showing:

```
Op Kill Tracker | vs OpponentName | MapName | Mode
──────────────────────────────────────────────────────────
[1] PlayerName1  |  OpName          |  ██ 3k / 2p
[2] PlayerName2  |  OpName          |  0k / 0p
[3] PlayerName3  |  OpName          |  █ 1k / 1p
[4] PlayerName4  |  OpName          |  0k / 0p
[5] PlayerName5  |  OpName          |  ██████ 7k / 3p
──────────────────────────────────────────────────────────
Last action: +1 kill PlayerName5 (total: 7)
[1-5] Kill  [q/w/e/r/t] Pull  [z] Undo  [x] End
```

The above is a rough layout reference, not a pixel-exact spec. Key elements:
- Header with session metadata
- One row per player: key binding, name, Op, visual bar + numeric count
- Last action feedback line (shows what the most recent keypress did)
- Keybinding legend at the bottom

The visual bar is optional polish — numeric count is the essential element. If the bar adds complexity, skip it.

### Keybindings

| Key | Action |
|-----|--------|
| `1` | Increment Player 1 kill count |
| `2` | Increment Player 2 kill count |
| `3` | Increment Player 3 kill count |
| `4` | Increment Player 4 kill count |
| `5` | Increment Player 5 kill count |
| `q` | Record Player 1 Op pull |
| `w` | Record Player 2 Op pull |
| `e` | Record Player 3 Op pull |
| `r` | Record Player 4 Op pull |
| `t` | Record Player 5 Op pull |
| `z` | Undo last action (kill or pull) |
| `x` or `Esc` | End session (with confirmation) |

### Undo behavior

- Maintain a stack of `(player_index, action_type)` tuples representing the order of actions.
- `z` pops the last entry and decrements that player's kill or pull count accordingly.
- If the stack is empty (nothing to undo), `z` is a no-op. Display "Nothing to undo" in the last action line.
- A player's count cannot go below 0 (defensive check, though the stack should prevent this naturally).

### Input handling

- Use `curses` non-blocking or half-delay input to capture single keypresses without requiring Enter.
- Ignore any keys not in the keybinding table — no error, just no-op.
- The display must update immediately after each valid keypress.

## Session End

When `x` or `Esc` is pressed:

1. Show a confirmation prompt: `End session and save? (y/n)`
2. If `n`, return to active tracking.
3. If `y`, write data to CSV and exit cleanly (restore terminal state via curses cleanup).

## CSV Output

### File

`op_kills.csv` in the project root directory. Append mode — if the file does not exist, create it with a header row. If it exists, append without re-writing headers.

### Schema

```
date,opponent,map,mode,player,operator,op_kills,op_pulls
```

### Row generation

One row per player per session = 5 rows appended per session.

| Column | Value |
|--------|-------|
| `date` | ISO 8601 date of the session (e.g., `2026-04-02`). Date when the tracking session is run, not the scrim date. |
| `opponent` | Opponent team name from session startup |
| `map` | Map name from session startup |
| `mode` | `HP` or `Control` |
| `player` | Player name from config |
| `operator` | Op name (default or overridden) |
| `op_kills` | Final kill count for this player in this session |
| `op_pulls` | Number of Op activations for this player in this session |

Write all 5 rows even if a player has 0 kills — this keeps the data complete and makes downstream analysis straightforward.

## Project Structure

```
op-kill-tracker/
├── pyproject.toml
├── config.json
├── op_kills.csv          (created on first run)
├── CLAUDE.md
└── src/
    └── tracker.py        (single-file application)
```

Keep it as a single Python file. This is a small utility — no need for multiple modules. The entry point should be runnable via `uv run python src/tracker.py` or equivalent.

## Out of Scope (for now)

- Global hotkey capture / background keystroke listening
- Mid-map Op switching (if a player changes Ops during a map, that's a manual config edge case to handle later)
- Google Sheets integration (CSV is the output for now)
- Timestamp logging of individual keypresses
- SQLite storage
- Web UI or GUI