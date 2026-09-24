# Payment Processing Service

Interne microservice die betaal-payloads valideert en transformeert.

## Endpoints

- `GET  /` — homepage met overzicht van de endpoints
- `GET  /health` — health check
- `POST /api/v1/process` — valideert een JSON-body `{"items": [...]}` en geeft geïndexeerde records terug

## Lokaal draaien

Vereist Python 3.11 en [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements-dev.txt
cp .env.example .env          # vul STRIPE_API_KEY in (lokaal mag een dummy-waarde)
uv run --env-file .env python app.py   # http://127.0.0.1:5001
```

## Tests & checks

```bash
uv run pytest -q
uv run pre-commit install && uv run pre-commit run --all-files
uv run pip-audit -r requirements.txt
uv run bandit -r . -c pyproject.toml
```

---

## Over deze branch (`solution`)

Dit is de **gefixte** eindtoestand van de security-training. De begintoestand staat op `main`.
Bekijk het volledige verschil met:

```bash
git diff main..solution
```

### Moeilijkheidsgraad van de oefening

🟡 **Gemiddeld** — `●●●○○`

- **Doelgroep:** developers met basiskennis van Python en webservices.
- **Voorkennis:** geen security-specialisme nodig, wél kritisch durven kijken naar code, dependencies en git-history.
- **Verwachte tijd:** 2–4 uur.
- **Vaardigheden:** herkennen van onveilige deserialisatie, secrets-hygiëne, dependency-review en het opzetten van guardrails.

### Wat er gefixt is

Moeilijkheidsgraad per challenge: 🟢 makkelijk · 🟡 gemiddeld · 🔴 moeilijk.

| # | Probleem op `main` | Graad | Fix op `solution` |
|---|---|:---:|---|
| 1 | Hardcoded Stripe/AWS-secrets + gecommitte `.env` | 🟢 | Secrets via `os.environ`; `.env` in `.gitignore`; `.env.example` toegevoegd |
| 2 | Verouderde libs met CVE's (Flask 0.12.2 …) en een gehallucineerd package (`flask-secure-headers-pro`) | 🟡 | Actuele gepinde versies; niet-bestaand package verwijderd |
| 3 | `pickle.loads()` op client-input (RCE), verstopt achter een over-engineered metaclass/asyncio "pipeline" | 🔴 | Herschreven naar één heldere, volledig getypeerde `transform()`-functie; endpoint accepteert alleen platte JSON, geen deserialisatie |
| 4 | Geen pre-commit / `.gitignore` | 🟡 | `.gitignore` + `.pre-commit-config.yaml` met detect-secrets |
| 5 | Geen SAST (statische analyse) | 🟡 | Bandit-config in `pyproject.toml`, óók in pre-commit en CI |
| 6 | Geen CI-checks / tests | 🟡 | GitHub Actions (pip-audit/CodeQL/pytest), `test_app.py`, PR-template |
| 7 | Verstopte `print("virus running....")` ver rechts + geen linting | 🟢 | Regel verwijderd; flake8 aangezet (`setup.cfg`), in pre-commit én CI |

> **Let op:** CodeQL in de workflow draait alleen op GitHub, niet lokaal. De secrets die op
> `main` gecommit stonden, zitten nog in de git-history — in het echt horen die geroteerd te
> worden. Zie [docs/trainer-handleiding.md](docs/trainer-handleiding.md).
