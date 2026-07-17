# Op Kill Tracker

A single-file browser tool for tallying Operator Skill kills per player during Call of Duty scrim VOD review.

Open `index.html` in a browser. Five players (Prevail, Viper, Abhiz, Warden, Skullguy) are mapped to keys **1–5** — click a card or press its number to add a kill. Backspace undoes the last kill.

Each match carries **Date, Week, Opponent, Map** metadata (entered once, above the counters). **Kills per minute** uses *real footage time*, not the in-game clock (which stops in the hill / between rounds). Read the match start and end timestamps off the VOD scrub bar, type them in (`mm:ss` or `h:mm:ss`), and the app divides kills by that duration. Scrub and rewind freely while tallying — nothing is timed live.

**Save match** snapshots the current tally into a saved-matches list (kept in `localStorage`) and clears the counters for the next map, keeping date/week/opponent so a series goes fast. **Download ops_kills.csv** exports every saved match:

```
Date,Week,Opponent,Map,Player,OpKills,FootageMin,OpKillsPerMin
```

This mirrors the key columns of `cdm_stats`'s `tournament_players.csv` — `(Date, Opponent, Map, Player)` — so it joins to those stats and slots into that dashboard. Dates are ISO (`YYYY-MM-DD`); opponent is a team abbreviation (`GAL`); re-exporting is safe since the cdm_stats loaders dedupe on the key.
