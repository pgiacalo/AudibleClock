#!/usr/bin/env python3
"""
Audible Clock — speaks the time every second using the system clock.

At the top of each minute it speaks the full time (e.g. "nine oh six PM").
For every other second it speaks just the count ("one", "two", ... "fifty-nine").

Zero dependencies: uses the operating system's built-in text-to-speech.
  - macOS   : the `say` command
  - Windows : PowerShell + System.Speech
  - Linux   : spd-say / espeak / festival (whichever is installed)

Run:   python3 clock_audible.py
Stop:  Ctrl-C
"""

import argparse
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty"]


def words(n):
    """Convert 0..59 to spoken words, e.g. 21 -> 'twenty-one'."""
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] if o == 0 else f"{TENS[t]}-{ONES[o]}"


def full_time_phrase(hour24, minute, use_24h=False):
    """Full spoken time, e.g. (21, 6) -> 'nine oh six PM'."""
    if use_24h:
        hour_words = words(hour24)
        suffix = ""
    else:
        ampm = "AM" if hour24 < 12 else "PM"
        h12 = hour24 % 12 or 12
        hour_words = words(h12)
        suffix = " " + ampm
    if minute == 0:
        minute_part = "o'clock"
    elif minute < 10:
        minute_part = "oh " + words(minute)
    else:
        minute_part = words(minute)
    return f"{hour_words} {minute_part}{suffix}"


class Speaker:
    """Non-blocking OS text-to-speech. Kills a still-speaking phrase before the
    next one so callouts never pile up (the analog of speechSynthesis.cancel())."""

    def __init__(self, rate=None, voice=None):
        self.system = platform.system()
        self.rate = rate
        self.voice = voice
        self.proc = None
        self.backend = self._detect_backend()

    def _detect_backend(self):
        if self.system == "Darwin" and shutil.which("say"):
            return "say"
        if self.system == "Windows":
            return "powershell"
        for cmd in ("spd-say", "espeak-ng", "espeak"):
            if shutil.which(cmd):
                return cmd
        if shutil.which("festival"):
            return "festival"
        return None

    def _command(self, text):
        b = self.backend
        if b == "say":
            cmd = ["say"]
            if self.voice:
                cmd += ["-v", self.voice]
            if self.rate:
                cmd += ["-r", str(self.rate)]
            cmd.append(text)
            return cmd, None
        if b == "powershell":
            rate_line = f"$s.Rate = {self.rate};" if self.rate is not None else ""
            voice_line = f"$s.SelectVoice('{self.voice}');" if self.voice else ""
            script = ("Add-Type -AssemblyName System.Speech;"
                      "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                      f"{voice_line}{rate_line}"
                      "$s.Speak([Console]::In.ReadToEnd());")
            return (["powershell", "-NoProfile", "-Command", script], text)
        if b in ("spd-say", "espeak-ng", "espeak"):
            cmd = [b]
            if b == "spd-say":
                cmd += ["-w"]  # wait so the kill-on-next-tick logic behaves
                if self.rate:
                    cmd += ["-r", str(self.rate)]
            elif self.rate:
                cmd += ["-s", str(self.rate)]
            cmd.append(text)
            return cmd, None
        if b == "festival":
            return (["festival", "--tts"], text)
        return None, None

    def speak(self, text):
        if not self.backend:
            print(f"[no TTS backend]  {text}")
            return
        # Cancel a phrase that is still speaking to avoid backlog.
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        cmd, stdin_text = self._command(text)
        try:
            if stdin_text is not None:
                self.proc = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.proc.stdin.write(stdin_text.encode("utf-8"))
                self.proc.stdin.close()
            else:
                self.proc = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:  # noqa: BLE001
            print(f"[TTS error: {e}]  {text}")


def run(use_24h=False, rate=None, voice=None):
    speaker = Speaker(rate=rate, voice=voice)
    if speaker.backend is None:
        print("Warning: no text-to-speech engine found; printing phrases only.")
        if platform.system() == "Linux":
            print("Install one with e.g.  sudo apt-get install espeak")
    else:
        print(f"Speaking via '{speaker.backend}'. Press Ctrl-C to stop.\n")

    last_second = -1
    try:
        while True:
            now = datetime.now()
            # Sleep until the next whole-second boundary of the system clock.
            time.sleep(max(0.0, 1.0 - now.microsecond / 1_000_000))
            now = datetime.now()
            s = now.second
            if s == last_second:
                continue  # guard against a double-fire within the same second
            last_second = s

            if s == 0:
                phrase = full_time_phrase(now.hour, now.minute, use_24h)
            else:
                phrase = words(s)

            stamp = now.strftime("%H:%M:%S")
            print(f"{stamp}  {phrase}", flush=True)
            speaker.speak(phrase)
    except KeyboardInterrupt:
        if speaker.proc and speaker.proc.poll() is None:
            speaker.proc.terminate()
        print("\nStopped.")


def main():
    p = argparse.ArgumentParser(description="Speak the time every second.")
    p.add_argument("--24h", dest="use_24h", action="store_true",
                   help="Use 24-hour format for the minute announcement.")
    p.add_argument("--rate", type=int, default=None,
                   help="Speech rate (backend-specific: macOS words/min ~200, "
                        "espeak words/min ~175, Windows -10..10).")
    p.add_argument("--voice", default=None,
                   help="Voice name (e.g. 'Samantha' on macOS). Backend-specific.")
    args = p.parse_args()
    run(use_24h=args.use_24h, rate=args.rate, voice=args.voice)


if __name__ == "__main__":
    sys.exit(main())
