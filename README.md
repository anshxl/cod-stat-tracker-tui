# Op Kill Tracker

A terminal-based keystroke counter for tracking Operator Skill kills and pulls during Call of Duty scrim VOD review.

The game provides no API or mechanism to track Op kills per player, so this tool runs in a focused terminal window alongside a VOD player. Press number keys to log kills and letter keys to log Op activations as you watch the VOD. Data is saved to CSV for downstream analysis like kills-per-pull averages across maps.

Built with Python and curses. Single-file, no external dependencies.
