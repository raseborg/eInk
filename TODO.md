# TODO – eInk Dashboard (Rasmus)

## Status
- [x] Fork + kloonaus `~/Sources/eInk` (raseborg/eInk → JuhaniS/eInk upstream)
  - 2026-05-18: siirretty `~/Documents/eInk` → `~/Sources/eInk` (iCloud korruptoi venviä jatkuvasti)
- [x] Dev-ympäristö: Python 3.14 venv + requirements.txt
- [x] `config.yaml` täytetty: koti, työ- ja perhekalenteri, HSL-avain, lähtötaulut
- [x] Ensimmäinen täysi preview-render: sää + kalenterit + HSL + uutiset toimii
- [x] HSL refaktoroitu reittisuunnittelusta lähtötaulu-malliin (config.hsl.boards)
- [x] Render-layout: TYÖ + PERHE-kalenterit erillisissä soluissa, HSL siirretty SÄÄ-sarakkeen alle
- [x] Upstream merge Juhanin uusimpiin committeihin (RRULE-tuki, partial refreshit)
- [x] Commit + push origin/main (raseborg/eInk)

## Seuraavaksi (Mac-dev)

### 1. eVaka-integraatio (BACKLOG)
Päiväkotisolu on configissa kommentoitu valmiiksi mutta tunnukset puuttuvat.
Vaiheessa 2026-05-18 testissä Espoon eVaka palautti `403 Forbidden` weak-login
-endpointista — joko tunnukset puuttuu tai endpoint on muuttunut.

- [ ] Lisää tunnukset `evaka.username` / `evaka.password` configiin
- [ ] Aja `python main.py --only evaka --no-cache` ja katso virhelogi
- [ ] Jos 403 jatkuu, tarkista että `evaka.base_url` on oikea
  (Espoo voi olla `https://espoonvarhaiskasvatus.fi` tai päivittynyt domain)
- [ ] Vertaa `data/evaka.py`:n login-URL nykyiseen eVaka-citizen-rajapintaan
  selaimen Network-tabista (kirjautumiskutsu)
- [ ] Kun toimii: PÄIVÄKOTI-solu (vasen ylä) korvautuu päivän tapahtumilla
- [ ] Myöhemmin kun lapsi siirtyy kouluun: korvaa Wilmalla (alempana)

### 2. Pi-asennus
Rauta käytössä (Pi Zero 2 WH + Waveshare 7.5" V2). Juhanin valmis ohje
[README.md](README.md):ssä "Deployment to Raspberry Pi" -osiossa.

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
