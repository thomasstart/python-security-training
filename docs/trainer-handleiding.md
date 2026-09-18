# Trainershandleiding — Python Security & AI-slop

Duur: ~90 minuten. Deelnemers werken op `main` en proberen richting `solution` te komen.

## Tijdsindeling

| Tijd | Onderdeel |
|------|-----------|
| 0-10 | Intro: "je hebt deze repo overgenomen". Repo clonen (in wegwerp-venv!). |
| 10-40 | Deelnemers zoeken zelf naar problemen. Nog geen hints. |
| 40-55 | Klassikaal: wie vond wat? Inventariseer op een bord. |
| 55-80 | Fixen. Verwijs naar `solution` alleen bij vastlopen. |
| 80-90 | Nabespreking: welke guardrail had elk probleem automatisch gevangen? |

## De zeven ingebouwde bevindingen

Zelfde nummering als in de [README](../README.md).

1. 🟢 **Secrets** — `STRIPE_API_KEY` / AWS-keys in `app.py` én een gecommitte `.env`.
   Guardrail: `detect-secrets` + `.gitignore` + GitHub secret scanning.
2. 🔴 **Gevaarlijke code** — de "async pipeline" doet `pickle.loads()` op client-input (remote
   code execution), verstopt achter een over-engineered metaclass/asyncio-constructie mét bare
   `except:` en zonder input-validatie. Les: complexiteit verbergt de bug — de fix (`transform()`)
   is korter, volledig getypeerd en valideert expliciet. Guardrail: `bandit` (B301) + code review.
3. 🟡 **Dependencies** — Flask 0.12.2 e.a. met bekende CVE's, plus een gehallucineerd package
   (`flask-secure-headers-pro`) dat niet op PyPI bestaat. Les: AI verzint plausibele
   packagenamen (slopsquatting-risico) — altijd verifiëren. Guardrail: `pip-audit` (SCA) in CI.
4. 🟡 **Pre-commit hooks** — geen `.gitignore` of `.pre-commit-config.yaml`; niets hield de
   secret of de `.env` tegen vóór de commit. Guardrail: `pre-commit` + `detect-secrets`-hook.
5. 🟡 **Bandit / SAST** — geen statische analyse aanwezig die `pickle.loads()` als high severity
   had gevlagd. Guardrail: `bandit`, vastgelegd in `pyproject.toml` en gedraaid in pre-commit en CI.
6. 🟡 **CI-pipeline & tests** — geen geautomatiseerde checks of tests bij elke push/PR.
   Guardrail: GitHub Actions (`pip-audit`, CodeQL, `pytest`) + PR-template.
7. 🟢 **Linting** — verstopte `print("Virus injection")` ver rechts in `app.py`, achter een muur
   van whitespace, en geen linter die dit zou hebben gevangen. Guardrail: `flake8` (E501/E702)
   in pre-commit en CI.

## Verwachte uitkomsten van de tools (voor jou als trainer)

- `bandit -r app.py` op **main**: findings B301 (pickle) en B105 (hardcoded password).
  Op **solution**: geen High/Medium.
- `pip-audit -r requirements.txt` op **main**: meerdere CVE's. Op **solution**: schoon.
- `pytest` bestaat alleen op **solution** en is groen (incl. de anti-pickle regressietest).

## Valkuilen tijdens de sessie

- Deelnemers die `requirements.txt` van main op hun host installeren. **Benadruk vooraf:
  alleen in een wegwerp-venv of container.**
- CodeQL draait alleen op GitHub, niet lokaal — dat is geen kapotte stap.
- Scommit-history: secrets verwijderen uit de working tree is niet genoeg; ze staan nog in
  de git-history. Bespreek `git filter-repo` / rotatie als vervolgonderwerp.
