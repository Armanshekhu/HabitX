# Habit Tracker — iOS (UIKit + Storyboard)

Native build of `Design/Habit_Tracker_iOS_UI.html`: Splash → Today → Statistics → New Habit → Rewards.

**Open `HabitTracker.xcodeproj` in Xcode 14+, pick your Team under *Signing & Capabilities*, run on an iPhone (iOS 15+).**
Designed at 390×844 (iPhone 14/15/16); layout is Auto Layout so other sizes adapt.

## What's in the storyboard
`Main.storyboard` holds all five screens with real Auto Layout constraints, outlets, actions and segues
(Splash ⇒ nav stack ⇒ Today → Statistics → Rewards, Today → New Habit). `LaunchScreen.storyboard` mirrors the splash.
Static UI (headers, cards, summary tiles, rewards copy, form, buttons) is laid out in the storyboard.
Data-driven parts (habit cards, 4-week heat-map, streak rows, badges, icon grid) are built in code from the store.

## Design fidelity
- All colours, font sizes/weights, radii, paddings and gaps are taken from the CSS (see `Theme.swift`).
- All 26 icons are drawn from the design's SVG path data at the original 24-unit grid and stroke widths (`IconData.swift`).
- Logo + app icon are rendered from the splash SVG geometry (`Assets.xcassets`).
- System font (SF Pro), dark mode forced, own nav row (system bar hidden, swipe-back kept).

## Behaviour (rules from the Rewards screen)
+10 XP per check-in (taken back on undo), +20 perfect-day bonus once/day, level = XP/100 + 1, streaks count scheduled days only,
badges earned once. State persists in UserDefaults. First launch seeds data that reproduces the mock exactly
(240 XP, Level 3, 3/5 done, streaks 12·5·8·3, This Week 71%, best 21).

## Notes
- New Habit opens pre-filled ("Morning Run", run icon, Mon–Fri) as in the mock. Clear the name for a blank form.
- Regenerate pieces: `tools/gen_icons.py`, `gen_assets.py`, `gen_storyboard.py`, `gen_pbxproj.py`; `tools/validate.py` checks storyboard ↔ Swift wiring.
