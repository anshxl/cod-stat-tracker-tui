# Op Kill Tracker — CLAUDE.md

## What this is

A single self-contained `index.html` for tallying Operator Skill kills per player during CoD scrim VOD review. No build, no deps, no server — open it in a browser.

## How it works

- 5 players (`Prevail, Viper, Abhiz, Warden, Skullguy`), mapped to keys `1`–`5`. Click a card or press its number to add a kill. Backspace undoes the last kill.
- Each match carries Date, Week, Opponent, Map metadata. Kills/min uses **real footage time**, not the in-game clock (which stops in the hill / between rounds). The user reads match start/end timestamps off the VOD scrub bar (`mm:ss` or `h:mm:ss`); the app divides kills by that duration. No live timer — rewinding/scrubbing while tallying doesn't affect the math.
- "Save match" snapshots the current tally into a `matches` list; "Download ops_kills.csv" exports all of them. State (`{ current, matches }`) persists in `localStorage` under key `op-kill-tracker`.

## CSV export — cdm_stats compatibility

Exports `ops_kills.csv` with header `Date,Week,Opponent,Map,Player,OpKills,FootageMin,OpKillsPerMin`, one row per player per match. The key columns mirror `~/Desktop/cdm_stats`'s `data/s2/tournament_players.csv` (`Date,Week,Opponent,Map,Player,...`) so it joins on `(Date, Opponent, Map, Player)` — Mode is derived from the map there, Week is optional. Dates are ISO; opponent is the team abbreviation. A cdm_stats loader would be a near-copy of `tournament_player_loader.py`. **That loader/dashboard wiring lives in cdm_stats, not here — not yet built.**

## Conventions

- Everything lives in `index.html` — markup, CSS, and JS in one file. Keep it that way unless it genuinely outgrows one file.
- Roster is the `PLAYERS` array in the script. Index = key mapping (index 0 = key `1`).

## Deliberately out of scope

Operator/pull tracking, per-map history, CSV export, multi-match sessions. The old Python/curses version tracked all of these and was too convoluted; this is the intentional rewrite that dropped them.
