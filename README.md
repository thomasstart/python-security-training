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

De uitgewerkte oplossing staat op de `solution`-branch. Kijk daar pas als je vastloopt:

```bash
git diff main..solution
```

### Het lek aantonen (optioneel, in een wegwerp-omgeving)

```bash
python app.py                       # terminal 1
python exploit/poc_deserialize.py   # terminal 2  -> schrijft /tmp/pwned.txt
```

Als dat bestand verschijnt, heeft de server code uitgevoerd die de client stuurde.
