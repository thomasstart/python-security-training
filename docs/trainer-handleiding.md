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

1. **Hardcoded secrets** — `STRIPE_API_KEY` / AWS-keys in `app.py` én een gecommitte `.env`.
   Guardrail: `detect-secrets` + `.gitignore` + GitHub secret scanning.
2. **Onveilige deserialisatie** — de "async pipeline" doet `pickle.loads()` op client-input.
   Dit is remote code execution. Guardrail: `bandit` (B301) + code review.
3. **Over-engineering / AI-slop** — metaclass + asyncio voor iets dat een functie van 3 regels is.
   Les: complexiteit verbergt de bug. De fix is *korter*.
4. **Verouderde dependencies** — Flask 0.12.2 e.a. met bekende CVE's.
   Guardrail: `pip-audit` (SCA) in CI.
5. **Gehallucineerd package** — `flask-secure-headers-pro` bestaat niet op PyPI.
   Les: AI verzint plausibele packagenamen (slopsquatting-risico). Altijd verifiëren.
6. **Geen foutafhandeling** — bare `except:` verbergt fouten; geen input-validatie.
   Guardrail: `flake8` (E722) + tests op edge cases.
7. **Geen guardrails** — geen `.gitignore`, pre-commit, CI, tests of PR-template.

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
