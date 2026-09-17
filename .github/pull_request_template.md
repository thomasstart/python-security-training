## Wat verandert er?

<!-- Korte beschrijving van de wijziging en waarom. -->

## Algemene checklist

- [ ] Tests toegevoegd/bijgewerkt en groen (`pytest`)
- [ ] `pre-commit run --all-files` slaagt lokaal
- [ ] Geen secrets in code, history of logs
- [ ] Dependencies gepind en `pip-audit` schoon

## Checklist voor AI-gegenereerde code

> Vul deze in als (een deel van) deze PR door een AI-assistent is geschreven.

- [ ] Ik begrijp **elke regel** en kan hem uitleggen — geen "het werkt, dus prima"
- [ ] Elk toegevoegd package bestaat **echt** op PyPI en is de bedoelde library
      (geen typo-/slopsquat; naam en downloads gecontroleerd)
- [ ] Geen onveilige deserialisatie (`pickle`, `yaml.load`, `marshal`) van
      untrusted input; geen `eval`/`exec`/`os.system` op input
- [ ] Complexiteit is gerechtvaardigd — geen metaclass/asyncio/abstractie waar
      een simpele functie volstaat
- [ ] Geen hardcoded secrets, tokens of endpoints; alles via env/config
- [ ] Foutafhandeling is expliciet — geen bare `except:` die fouten verbergt
