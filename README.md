# Payment Processing Service

Interne microservice die betaal-payloads verwerkt en wisselkoersen ophaalt.

## Endpoints

- `GET  /` — homepage met overzicht van de endpoints
- `GET  /health` — health check
- `POST /api/v1/process` — verwerkt een base64-payload via de processing pipeline
- `GET  /api/v1/rate` — haalt actuele koersen op bij de upstream provider

## Lokaal draaien

Vereist Python 3.11 en [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uv run python app.py
```

---

## ⚠️ Trainingsoefening — lees dit eerst

Deze repo is **bewust onveilig**. Het is het startpunt van een security-training.

> **Installeer `requirements.txt` NIET op je werkmachine.** De versies bevatten bekende
> kwetsbaarheden en er staat een verzonnen ("gehallucineerd") package tussen. Gebruik een
> wegwerp-venv of een container.

### Opdracht

Je hebt zojuist deze repo overgenomen van een collega die veel met een AI-assistent werkte.
Je taak: maak hem productieklaar. Werk op een nieuwe branch en open een PR.

Vind en fix alles wat mis is. Denk in lagen:

1. **Secrets** — staat er iets in de code of in git dat er niet hoort?
2. **Gevaarlijke code** — de "processing pipeline" ziet er indrukwekkend uit. Snap je écht
   wat hij doet? Wat gebeurt er als een aanvaller de payload bepaalt?
3. **Dependencies** — kloppen de versies? Bestaat elk package echt?
4. **Guardrails** — wat had dit ooit tegen moeten houden? (denk aan `.gitignore`,
   pre-commit hooks, CI-checks, tests, een PR-template)

### Pointers per laag

Nog niet eerder met security gewerkt? Geen probleem. Hieronder staat per laag waar je op let,
welke tools je helpen en een paar concrete hints. Klap de hints pas open als je even vastzit.
Werk bij voorkeur in deze volgorde en maak per laag een aparte commit, dan blijft je PR goed
te reviewen.

#### 1. Secrets 🟢

**Waar je op let:** API-keys, wachtwoorden en tokens horen nooit in de code of in git. Iedereen
met leestoegang tot de repo (of een gelekte kopie) kan ze gebruiken.

**Probeer:**

```bash
grep -rnE "KEY|SECRET|TOKEN|PASSWORD" --exclude-dir=.venv .
git ls-files                    # welke bestanden zitten écht in git?
git log --oneline -- .env       # en sinds wanneer?
```

<details>
<summary>Hint</summary>

- Kijk bovenaan in `app.py` en in `.env`.
- Lees secrets in via een omgevingsvariabele: `os.environ["STRIPE_API_KEY"]`. Zo crasht de app
  meteen met een duidelijke fout als de variabele ontbreekt, en draait hij niet stilletjes met
  een lege key.
- Haal `.env` uit git met `git rm --cached .env`, zet het in een `.gitignore` en voeg een
  `.env.example` toe met nep-waarden, zodat collega's weten welke variabelen nodig zijn.
- **Belangrijk:** een secret verwijderen in een nieuwe commit is niet genoeg. Hij staat nog in
  de git-history. In het echt moet je de key dus **roteren** (intrekken en een nieuwe maken).
  Zet dat in je PR-beschrijving.

</details>

#### 2. Gevaarlijke code 🔴

**Waar je op let:** laat je niet afleiden door ingewikkelde constructies (metaclasses, asyncio,
decorators). Volg gewoon wat er met de input van de gebruiker gebeurt, van `request` tot het
eind. Vraag je bij elke stap af: *wat als een aanvaller deze waarde kiest?*

**Probeer:** zet een paar `print()`-regels in de pipeline of loop er met een debugger doorheen.
Welke stappen worden uitgevoerd, en in welke volgorde?

<details>
<summary>Hint 1: waar zit het probleem?</summary>

Uiteindelijk doet de hele pipeline maar twee dingen: `base64.b64decode()` en daarna
`pickle.loads()`. Zoek eens op wat de Python-documentatie over `pickle` zegt
([waarschuwing bovenaan de pagina](https://docs.python.org/3/library/pickle.html)).

</details>

<details>
<summary>Hint 2: waarom is dat zo erg?</summary>

Met `pickle` kan een object bij het uitpakken zélf bepalen welke functie er wordt aangeroepen
(via `__reduce__`). Wie de payload stuurt, kan dus willekeurige code op je server uitvoeren
(*Remote Code Execution*). Kijk in `exploit/poc_deserialize.py` hoe dat werkt, en zie
[Het lek aantonen](#het-lek-aantonen-optioneel-in-een-wegwerp-omgeving) hieronder.

</details>

<details>
<summary>Hint 3: hoe fix je het?</summary>

- Deserialiseer nooit ongecontroleerde input met `pickle` (en ook niet met `yaml.load` zonder
  `SafeLoader`, of met `eval`).
- Laat het endpoint gewone JSON accepteren (`request.get_json()`) en **valideer** die: is het
  een dict, zitten de verwachte velden erin, hebben ze het juiste type? Geef anders een `400`
  terug.
- Vervang de metaclass/asyncio-constructie door één simpele functie. Code die je niet kunt
  uitleggen, kun je ook niet reviewen.
- Kijk ook even naar de rest van `app.py`: `debug=True`, `host="0.0.0.0"`, een kale `except:`
  en een `requests.get()` zonder `timeout`. Wat betekenen die in productie?

</details>

#### 3. Dependencies 🟡

**Waar je op let:** oude versies hebben bekende kwetsbaarheden (CVE's). En AI-assistenten
verzinnen soms packages die niet bestaan. Een aanvaller kan zo'n naam registreren en er
malware in stoppen (*slopsquatting*).

**Probeer:**

```bash
uv pip install pip-audit
uv run pip-audit -r requirements.txt     # welke CVE's zijn bekend?
```

Zoek elk package op [pypi.org](https://pypi.org) op. Bestaat het? Wie onderhoudt het? Wanneer
kwam de laatste release uit?

<details>
<summary>Hint</summary>

- Eén package in `requirements.txt` bestaat helemaal niet op PyPI. Verwijder het.
- Werk de rest bij naar de nieuwste versie en **pin** die (`==`), zodat iedereen hetzelfde
  installeert. Draai `pip-audit` opnieuw tot er niets meer gevonden wordt.
- Tip: zet tools die je alleen tijdens het ontwikkelen gebruikt (pytest, bandit, …) in een
  apart `requirements-dev.txt`.

</details>

#### 4. Guardrails 🟡

**Waar je op let:** alles hierboven is door een mens (of een AI) gemaakt en door niemand
tegengehouden. Hoe voorkom je dat het de volgende keer weer gebeurt? Zoek maatregelen die
**automatisch** afgaan, zodat het niet afhangt van iemand die er toevallig aan denkt.

<details>
<summary>Hint: welke lagen kun je toevoegen?</summary>

| Maatregel | Wat het tegenhoudt | Tool |
|---|---|---|
| `.gitignore` | `.env`, `.venv`, `__pycache__` in git | – |
| Pre-commit hooks | Secrets en fouten vóórdat ze gecommit worden | [pre-commit](https://pre-commit.com) + [detect-secrets](https://github.com/Yelp/detect-secrets) |
| Statische analyse (SAST) | Gevaarlijke patronen zoals `pickle.loads` en `debug=True` | [bandit](https://bandit.readthedocs.io): `uv run bandit -r app.py` |
| Linting | Rommelige of verdachte code | flake8 |
| Tests | Regressies: werkt het endpoint, weigert het foute input? | pytest |
| CI-pipeline | Alles hierboven, maar dan op élke PR | GitHub Actions |
| PR-template | Een checklist voor de reviewer | `.github/pull_request_template.md` |

Begin klein. Een `.gitignore` en één pre-commit hook zijn al veel beter dan niets. Draai
`bandit` eens op de **originele** `app.py`: had hij het lek gevonden?

</details>

### Klaar? Check jezelf

- [ ] `grep` vindt geen secrets meer in de code, en `.env` staat niet meer in git
- [ ] Een request met de exploit-payload geeft een nette fout en voert geen code uit
- [ ] `pip-audit -r requirements.txt` vindt niets
- [ ] `bandit -r app.py` vindt geen issues met hoge ernst
- [ ] Er zijn tests, en die slagen
- [ ] Je PR-beschrijving legt per probleem uit **wat** er mis was en **waarom** je fix werkt

De uitgewerkte oplossing staat op de `solution`-branch. Kijk daar pas als je vastloopt:

```bash
git diff main..solution
```

### Het lek aantonen (optioneel, in een wegwerp-omgeving)

```bash
python app.py                       # terminal 1
python exploit/poc_deserialize.py   # terminal 2  -> schrijft /tmp/pwned.txt
```

> **macOS:** poort 5000 wordt vaak gebruikt door AirPlay Receiver (je krijgt dan een `403`).
> Zet AirPlay Receiver uit in Systeeminstellingen, of draai de app op een andere poort en
> gebruik `TARGET=http://localhost:<poort>/api/v1/process python exploit/poc_deserialize.py`.

Als dat bestand verschijnt, heeft de server code uitgevoerd die de client stuurde.
