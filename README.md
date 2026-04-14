# E-ink Dashboard

A home dashboard for a Waveshare 7.5" e-ink display (800×480), running on a Raspberry Pi. Displays weather, calendar events, news headlines, waste collection schedule, daycare events, and public transit departures.

## Layout

```
┌──────────────────┬──────────────────┬──────────────────┐
│  PÄIVÄKOTI       │  KALENTERI       │  SÄÄ + PVM/KELLO │
│  Daycare events  │  Calendar events │  Weather         │
├──────────────────┼──────────────────┼──────────────────┤
│  SÄHKÖ           │  HSL             │  JÄTEHUOLTO      │
│  Electricity     │  Transit         │  Waste schedule  │
├──────────────────┴──────────────────┴──────────────────┤
│  UUTISET  (full width, 2 headlines)                    │
└────────────────────────────────────────────────────────┘
```

## Hardware

| Part | Model | Notes |
|---|---|---|
| Display | Waveshare 7.5" e-Paper HAT V2 (800×480) | Black/white |
| Computer | Raspberry Pi Zero 2 W (or any Pi with 40-pin GPIO) | Needs pre-soldered headers |
| Power | 5V micro-USB charger, ≥1A | Standard phone charger works |

> **Important:** The Raspberry Pi Zero 2 W is sold both with and without GPIO headers.
> The Waveshare HAT has a female connector and requires **male pins** on the Pi.
> Make sure to buy the **"with headers" (WH) version**, or solder a 2×20 male header yourself.

## Data sources

| Module | Source | Auth |
|---|---|---|
| Weather | [Open-Meteo](https://open-meteo.com/) | None |
| Calendar | Google Calendar iCal | Secret URL token |
| News | YLE Uutiset RSS | None |
| Waste | Manual schedule in config | None |
| Daycare | Espoo eVaka (`/api/citizen/auth/weak-login`) | Username + password |
| Transit | [HSL Digitransit v2 GraphQL](https://portal-api.digitransit.fi/) | API key |

## Development setup (macOS)

### 1. Clone and create virtualenv

```bash
git clone <repo>
cd eInk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your credentials and location. The file contains passwords and API keys — do not commit it.

Key settings:

```yaml
location:
  latitude: 60.1699
  longitude: 24.9384
  name: "Helsinki"

hsl:
  api_key: "your-key-from-portal-api.digitransit.fi"
  to_name: "Pasila"
  to_lat: 60.1985
  to_lon: 24.9323
  min_walk_bus: 3       # minutes to nearest bus stop
  min_walk_rail: 15     # minutes to nearest train station

waste:
  collections:
    - type: "Sekajäte"
      interval_weeks: 2
      next_date: "2026-03-25"
    - type: "Biojäte"
      interval_weeks: 4
      next_date: "2026-03-16"
```

### 3. Google Calendar iCal link

In Google Calendar: *Calendar settings → "Private address in iCal format"*. Add the URL to `config.yaml`:

```yaml
calendars:
  - name: "Oma"
    ical_url: "https://calendar.google.com/calendar/ical/.../basic.ics"
```

### 4. HSL API key

Register at [portal-api.digitransit.fi](https://portal-api.digitransit.fi/) and create a subscription for the Routing API. Add the key to `config.yaml`.

### 5. Run

```bash
source venv/bin/activate

# Full run, open preview on macOS
python main.py --preview

# Force data refresh (skip cache)
python main.py --no-cache --preview

# Test a single module
python main.py --only weather
python main.py --only hsl --no-cache
```

## Raspberry Pi deployment

### 1. Flash SD card

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/):
- OS: Raspberry Pi OS Lite (64-bit)
- Enable SSH, set username/password, configure WiFi (country: FI)

### 2. Connect display

Attach the Waveshare HAT to the 40-pin GPIO header with the Pi powered off.

### 3. Enable SPI

```bash
ssh -t USER@HOSTNAME "sudo raspi-config nonint do_spi 0"
```

### 4. Install system dependencies

```bash
ssh -t USER@HOSTNAME "sudo apt install -y git python3-venv python3-pip swig liblgpio-dev"
```

### 5. Sync project files from Mac

```bash
./sync.sh
```

Or manually:
```bash
rsync -av --exclude venv --exclude cache --exclude output --exclude .git \
  /path/to/eInk/ USER@HOSTNAME:~/eInk/
```

### 6. Set up virtualenv and install Python dependencies

```bash
ssh USER@HOSTNAME "cd ~/eInk && python3 -m venv venv && venv/bin/pip install -r requirements.txt"
```

Then install the Waveshare e-Paper library (not on PyPI — must be cloned from GitHub):

```bash
ssh USER@HOSTNAME "cd ~/eInk && git clone https://github.com/waveshare/e-Paper waveshare-epaper && venv/bin/pip install ./waveshare-epaper/RaspberryPi_JetsonNano/python/"
```

### 7. Create required directories

```bash
ssh USER@HOSTNAME "mkdir -p ~/eInk/cache ~/eInk/output"
```

### 8. Copy config

```bash
scp config.yaml USER@HOSTNAME:~/eInk/config.yaml
```

### 9. Test

```bash
ssh USER@HOSTNAME "cd ~/eInk && venv/bin/python main.py --no-cache"
```

### 10. Set up cron

```bash
ssh -t USER@HOSTNAME "crontab -e"
```

Add (replace `juhani` with your username):
```
@reboot sleep 30 && cd /home/juhani/eInk && venv/bin/python main.py >> /tmp/eink.log 2>&1
*/10 * * * * cd /home/juhani/eInk && venv/bin/python main.py >> /tmp/eink.log 2>&1
```

### Sync changes from Mac

```bash
./sync.sh
```

## Project structure

```
eInk/
├── main.py              # Entry point, CLI args, module orchestration
├── render.py            # Pillow-based image renderer (800×480, grayscale)
├── config.yaml          # Your config (not committed)
├── config.example.yaml  # Template
├── data/
│   ├── weather.py       # Open-Meteo
│   ├── calendar.py      # iCal / Google Calendar
│   ├── news.py          # YLE RSS feed
│   ├── electricity.py   # Caruna / pycaruna
│   ├── waste.py         # Manual waste schedule
│   ├── evaka.py         # Espoo daycare (eVaka)
│   └── hsl.py           # HSL Digitransit transit
├── display/
│   ├── simulator.py     # PNG output for macOS development
│   └── epaper.py        # Waveshare 7.5" v2 driver (Raspberry Pi)
├── fonts/               # Optional: place Inter-Regular.ttf + Inter-Bold.ttf here
├── cache/               # JSON cache files (auto-generated)
└── output/              # Output PNG (auto-generated, macOS only)
```

## Caching

Each module writes a JSON cache file under `cache/`. TTLs are configurable per module in `config.yaml`. Stale cache is used as a fallback when an API call fails — the dashboard always shows something even when offline.

```yaml
cache:
  ttl_minutes: 55           # weather, calendar
  hsl_ttl_minutes: 10       # real-time transit
  hsl_active_hours: [6, 22] # no HSL fetches outside these hours
  evaka_ttl_minutes: 1440   # daycare: once per day
  electricity_ttl_minutes: 720
```
