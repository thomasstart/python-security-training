# Payment Processing Service

Interne microservice die betaal-payloads valideert en transformeert.

## Endpoints

- `GET  /health` — health check
- `POST /api/v1/process` — valideert een JSON-body `{"items": [...]}` en geeft geïndexeerde records terug

## Lokaal draaien

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # vul echte waarden in (staat in .gitignore)
export STRIPE_API_KEY=...     # of via .env-loader
python app.py
```

## Tests & checks

```bash
pytest -q
pre-commit install && pre-commit run --all-files
pip-audit -r requirements.txt
bandit -r . -c pyproject.toml
```

---

## Over deze branch (`solution`)

Dit is de **gefixte** eindtoestand van de security-training. De begintoestand staat op `main`.
Bekijk het volledige verschil met:

```bash
git diff main..solution
```

### Wat er gefixt is

| # | Probleem op `main` | Fix op `solution` |
|---|---|---|
| 1 | Hardcoded Stripe/AWS-secrets + gecommitte `.env` | Secrets via `os.environ`; `.env` in `.gitignore`; `.env.example` toegevoegd |
| 2 | `pickle.loads()` op client-input (RCE) | Endpoint accepteert alleen platte JSON; geen deserialisatie |
| 3 | Over-engineered metaclass/asyncio "pipeline" | Herschreven naar één heldere `transform()`-functie |
| 4 | Verouderde libs met CVE's (Flask 0.12.2 …) | Actuele gepinde versies |
| 5 | Gehallucineerd package `flask-secure-headers-pro` | Verwijderd (bestond niet op PyPI) |
| 6 | Geen type hints / bare `except:` | Volledige type hints + expliciete validatie en 4xx-responses |
| 7 | Geen guardrails | `.gitignore`, pre-commit, GitHub Actions (bandit/pip-audit/CodeQL/pytest), tests, PR-template |

> **Let op:** CodeQL in de workflow draait alleen op GitHub, niet lokaal. De secrets die op
> `main` gecommit stonden, zitten nog in de git-history — in het echt horen die geroteerd te
> worden. Zie [docs/trainer-handleiding.md](docs/trainer-handleiding.md).
