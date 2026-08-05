# Audible Clock

A single-page web app that speaks the time every second using your computer's system clock.

- At the top of each minute it speaks the full time, e.g. **"nine oh six PM"** (12-hour, AM/PM).
- For every other second it speaks just the count: **"one, two, three… fifty-nine"**.

## Use it

Live page: **https://pgiacalo.github.io/AudibleClock/**

Press **▶ Start** to enable audio (browsers block sound until you click), then leave the tab open and awake.

Or run locally by opening `index.html` in any modern browser.

## Notes

- Uses the browser's built-in Web Speech API — no install, works on Mac/PC/Linux.
- Includes a voice picker and a live on-screen clock.
- Keep the tab visible and the machine awake; browsers throttle background timers.
