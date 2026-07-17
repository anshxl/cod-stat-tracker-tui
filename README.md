# Op Kill Tracker

A single-file browser tool for tallying Operator Skill kills per player during Call of Duty scrim VOD review.

Open `index.html` in a browser. Five players (Prevail, Viper, Abhiz, Warden, Skullguy) are mapped to keys **1–5** — click a card or press its number to add a kill. Backspace undoes the last kill.

Each match carries **Date, Week, Opponent, Map** metadata (entered once, above the counters). **Kills per minute** uses *real footage time*, not the in-game clock (which stops in the hill / between rounds). Read the match start and end timestamps off the VOD scrub bar, type them in (`mm:ss` or `h:mm:ss`), and the app divides kills by that duration. Scrub and rewind freely while tallying — nothing is timed live.

**Save match** snapshots the current tally into a saved-matches list (kept in `localStorage`) and clears the counters for the next map, keeping date/week/opponent so a series goes fast. Click a saved match to reopen it for editing (fix timestamps, etc.) with its kills intact.

The export is `ops_kills.csv`:

```
Date,Week,Opponent,Map,Player,OpKills,FootageMin,OpKillsPerMin
```

This mirrors the key columns of `cdm_stats`'s `tournament_players.csv` — `(Date, Opponent, Map, Player)` — so it joins to those stats and slots into that dashboard. Dates are ISO (`YYYY-MM-DD`); opponent is a team abbreviation (`GAL`); re-writing is safe since the cdm_stats loaders dedupe on the key.

### Syncing to one file

**Link / sync CSV** (Chrome/Edge) links a single file once — point it at `cdm_stats/data/s2/ops_kills.csv` — and from then on every Save/edit/delete writes the *full history* to that exact file automatically. No download step, no `~/Downloads` clutter, and the file is durable rather than living only in the browser. The whole file is rewritten each time (not appended) so edits can't create duplicate rows. Browsers require re-granting file permission with one click each session, so click **Link / sync CSV** once after reopening the page. **Download ops_kills.csv** is the fallback for other browsers or manual placement.
