# Op Kill Tracker

A single-file browser tool for tallying Operator Skill kills per player during Call of Duty scrim VOD review.

Open `index.html` in a browser. Five players (Prevail, Viper, Abhiz, Warden, Skullguy) are mapped to keys **1–5** — click a card or press its number to add a kill. Backspace undoes the last kill.

**Kills per minute** uses *real footage time*, not the in-game clock (which stops in the hill / between rounds). Read the match start and end timestamps off the VOD scrub bar, type them in (`mm:ss` or `h:mm:ss`), and the app divides kills by that duration. Scrub and rewind freely while tallying — nothing is timed live.

State (kills, timestamps) persists in `localStorage`. "Reset match" clears it.
