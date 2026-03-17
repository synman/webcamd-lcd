# 📟 webcamd-lcd — PiOLED Stats Display

> forge ❯ bambu ❯ **wcdl** · application
>
> **Archetype:** Hardware display driver (I2C OLED)
> **Language:** Python 3
> **Interfaces:** I2C (SSD1306 128x32 OLED) · HTTP client (polls webcamd)
> **Depends on:** 📹 webcamd — HTTP stats endpoint
> **Shared rules:** `~/ai/forge/bambu/.claude/rules/bambu-ecosystem.md`

## Build / Validate

No build system, tests, or linting.

## Architecture

- Adafruit SSD1306 128x32 I2C OLED, CircuitPython busio
- Target platform: Raspberry Pi (hardcoded `/home/pi/lcdstats/`)
- 1-bit monochrome PIL rendering
- Polls webcamd HTTP stats endpoint
- Dependencies: `requests`, `Pillow`, `adafruit_ssd1306`, `board`/`busio` (I2C)

## Git Policy

Agent-managed. Full git lifecycle authorized: stage, commit, push.
