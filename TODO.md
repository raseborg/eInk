# TODO – eInk Dashboard (Rasmus)

## Status
- [x] Fork + kloonaus `~/Documents/eInk` (raseborg/eInk → JuhaniS/eInk upstream)
- [x] Dev-ympäristö: Python 3.14 venv + requirements.txt
- [x] `config.yaml` luotu placeholdereilla
- [x] Ensimmäinen emulointiajo: sää + YLE toimii, output/dashboard.png syntyy

## Seuraavaksi (Mac-dev)

### 1. Täytä konfig
Muokkaa [config.yaml](config.yaml):
- [ ] `location.latitude` / `longitude` — oma koti (nyt Espoo ~Matinkylä)
- [ ] `calendars[0].ical_url` — Google Calendar → Asetukset → "Salainen osoite iCal-muodossa"
- [ ] `evaka.username` / `password` — Espoon eVaka-tunnukset
- [ ] `hsl.api_key` — hae ilmainen avain https://portal-api.digitransit.fi/
- [ ] `hsl.to_name` / `to_lat` / `to_lon` — määränpää (esim. työpaikka)

Testaa moduuli kerrallaan:
```bash
cd ~/Documents/eInk && source venv/bin/activate
python main.py --only calendar --no-cache
python main.py --only hsl --no-cache
python main.py --only evaka --no-cache
python main.py --preview --no-cache   # koko dashboard + avaa PNG
```

### 2. Laitteisto (tilattu AliExpressistä 2026-04-21)

- [x] **Pi Zero 2 WH** (with headers) — yhteensopiva suoraan
- [x] **Waveshare 7.5" e-Paper HAT V2** (800×480, B/W) — Juhanin koodin olettama malli
- [ ] MicroSD 16–32 GB A1 (SanDisk/Samsung) — tarvitaanko? Katso jääkö varastosta
- [ ] 5V micro-USB laturi ≥1A — useimmilla jo puhelinlaturi
- [ ] Kotelo / kehys (myöhemmin, 3D-print tai puu)

AliExpress-toimitus tyypillisesti 2–4 viikkoa EU:hun. Kun osat saapuu → Pi-asennus alla.

### 3. Pi-asennus (kun osat saapuvat)
Juhanilla valmis ohje [README.md](README.md):ssä "Deployment to Raspberry Pi" -osiossa.
Oleellista: `raspi-config` → SPI päälle, `./sync.sh` (muokkaa kohde `pi@eink.local`), cron joka 10 min.

## Myöhemmät moduulit

### Wilma (koulun kalenteri)
Kun lapsi siirtyy perusopetukseen → korvaa/täydentää eVakan.

**Suunnitelma:**
- [ ] Lisää `data/wilma.py` samassa `fetch(config, use_cache)` -muodossa kuin muut
- [ ] Wilma käyttää kouluspesifistä URL:a, esim. `https://espoo.inschool.fi/`
- [ ] Kirjautuminen: POST `/login` käyttäjätunnuksella + salasanalla, saadaan session-eväste
- [ ] Hae `/news` tai `/calendar` endpointeista (Wilma-API on kouluspesifinen, kokeile browser dev-toolsilla)
- [ ] Palauta sama dict-rakenne kuin `calendar.py`: `{ "events": [{ "start": ISO, "title": str, "description": str }] }`
- [ ] Lisää `main.py`:hen `wilma`-moduulin ehdollinen fetch (`if config.get("wilma", {}).get("username"):`)
- [ ] Lisää `render.py`:hen Wilma-solun rendaus (voi jakaa `evaka`-solun tilaa tai korvata se)

**Kirjastovihjeitä:**
- [matnieminen/wilma-scraper](https://github.com/matnieminen/wilma-scraper) (Python, tarkista onko ajan tasalla)
- Visma InSchool -API:sta ei ole virallista oppilasdokumentaatiota — toimitaan screen-scrapingillä tai app-API:lla

### Muut parannukset
- [ ] Säähän 3-päivän ennustestrippi (CLAUDE.md mainitsee tämän)
- [ ] Sähköhintasolu (Pörssisähkö) jos sähkön seuranta kiinnostaa — korvaa Caruna-solu
- [ ] Päivittäinen viestintuntumapalkki (esim. Kalenterin päivän tärkein)

## Upstream-päivitykset
Juhanin repon uudet commitit:
```bash
cd ~/Documents/eInk
git fetch upstream
git log --oneline main..upstream/main   # mitä uutta
git merge upstream/main                  # tai cherry-pick valikoidusti
```
