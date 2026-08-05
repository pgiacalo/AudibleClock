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

## Python version (`clock_audible.py`)

A terminal version with the same behavior. Unlike the browser, it keeps talking
even when it's not the focused window and needs no click to start.

```bash
python3 clock_audible.py        # Ctrl-C to stop
```

- **Zero dependencies** — uses the OS's built-in text-to-speech:
  macOS `say`, Windows PowerShell/System.Speech, Linux `espeak`/`spd-say`
  (install one on Linux, e.g. `sudo apt-get install espeak`).
- Options:
  - `--24h` — 24-hour minute announcement (e.g. "twenty-one oh six")
  - `--voice NAME` — pick a voice (e.g. `--voice Samantha` on macOS)
  - `--rate N` — speech rate (backend-specific)
