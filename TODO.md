# TODO – eInk Dashboard (Rasmus)

## Status
- [x] Fork + kloonaus `~/Sources/eInk` (raseborg/eInk → JuhaniS/eInk upstream)
  - 2026-05-18: siirretty `~/Documents/eInk` → `~/Sources/eInk` (iCloud korruptoi venviä jatkuvasti)
- [x] Dev-ympäristö: Python 3.14 venv + requirements.txt
- [x] `config.yaml` täytetty: koti, työ- ja perhekalenteri, HSL-avain, lähtötaulut, **eVaka-tunnukset**
- [x] Ensimmäinen täysi preview-render: kaikki kuusi solua tuottavat dataa (sää, työ, perhe, päiväkoti, HSL, uutiset)
- [x] HSL refaktoroitu reittisuunnittelusta lähtötaulu-malliin (config.hsl.boards)
- [x] Render-layout: PÄIVÄKOTI vasen sarake täysikorkeana (Alice/Mikael näkyy), TYÖ/PERHE keskellä, SÄÄ/HSL oikealla
- [x] eVaka-integraatio toimii: `/api/citizen/children` UUID → etunimi -mappaus
- [x] Upstream merge Juhanin uusimpiin committeihin (RRULE-tuki, partial refreshit)
- [x] Commit + push origin/main (raseborg/eInk)
- [x] 2026-05-19: ostettu väärä rauta AliExpressistä — 7.5" (B) 3-värinen + HAT puuttui pakkauksesta
- [x] 2026-06-04: tilattu korvaava rauta Welectronista (Saksa) — Waveshare 13504 7.5" e-Paper HAT V2 (B/W, 800×480), 64,90 € + posti. ETA n. 9.–11.6.

## Seuraavaksi (Mac-dev)

### 1. Pi-asennus (paketin saapumista odottaen)
Rauta tilattu Welectronista 2026-06-04. ETA Suomeen n. 9.–11.6.
Kun paketti saapuu, aja allaoleva sekvenssi (~30–45 min):

- [ ] Flashaa SD-kortti Raspberry Pi Imagerilla (OS Lite 64-bit, SSH, WiFi FI, hostname `eink`)
- [ ] Kytke HAT virrat-pois Pi:hin, boot, `ping eink.local`
- [ ] SSH: `sudo raspi-config nonint do_spi 0`, apt-asennukset
- [ ] `./sync.sh` Mäkistä Pi:hin (muokkaa kohde `pi@eink.local`)
- [ ] `python3 -m venv venv && venv/bin/pip install -r requirements.txt`
- [ ] `scp config.yaml pi@eink.local:~/eInk/config.yaml`
- [ ] Ensimmäinen ajo `venv/bin/python main.py --no-cache` → e-ink vilkkuu, kuva näkyy
- [ ] `./sync_cron.sh` cron päälle (3 rytmiä)

Test-komennot Mäkillä:
```bash
cd ~/Sources/eInk && source venv/bin/activate
python main.py --only calendar --no-cache
python main.py --only hsl --no-cache
python main.py --only evaka --no-cache
python main.py --preview --no-cache   # koko dashboard + avaa PNG
```

### 3. Laitteistotarvikkeet
- [x] **Pi Zero 2 WH** (with headers) — saapunut 2026-05-18
- [x] **Waveshare 7.5" e-Paper HAT V2** (800×480, B/W) — saapunut 2026-05-18
- [ ] MicroSD 16–32 GB A1 (SanDisk/Samsung) — tarkista varastosta
- [ ] 5V micro-USB laturi ≥1A — puhelinlaturi käy
- [ ] Kotelo / kehys (myöhemmin, 3D-print tai puu)

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
cd ~/Sources/eInk
git fetch upstream
git log --oneline main..upstream/main           # mitä uutta
git merge upstream/main --no-edit               # tuo sisään ilman editoria
```

**Vinkki:** käytä aina `--no-edit` ettei vim aukea. Jos editori silti aukeaa
ja jää jumiin, tapa toisesta terminaalista: `killall vi`, sitten
`git merge --abort` ja yritä uudestaan `--no-edit`-lipulla.
