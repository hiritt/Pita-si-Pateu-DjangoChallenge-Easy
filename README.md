# General Deadlock — Django War Simulator (Easy)

Complete Django implementation for all four tasks of the CodeRun easy challenge. **This is Django, not Flask.** Uses the built-in SQLite database and plain Django templates; no JavaScript frameworks required.

## Start in PyCharm (Windows / PowerShell)

1. Extract this ZIP and use **File → Open** to open the extracted folder **containing `manage.py`** in PyCharm. Use your Python `.venv` as the interpreter (Python 3.15 works with Django 6.1.3).
2. In the project terminal, run:

   ```powershell
   python -m pip install -r requirements.txt
   python manage.py migrate
   python manage.py test
   python manage.py runserver
   ```

3. Visit **http://127.0.0.1:8000/unit** to add fighters, then **http://127.0.0.1:8000/unit/all** to view, heal, simulate, and view stats. Click a fighter for details and fight history.

**Do not run `main.py`**. For Django the entry point is `manage.py`.

## Requirements checklist

- [x] **1 — `/unit`**: Fighter form for Name, Type, Team, Health (0–100, default 100), AttackPoints (0–50), ProfileImageLink (URL). Django `ModelForm` validates input; success and error messages display; data is saved to SQLite.
- [x] **2 — `/unit/all` and `/unit/<id>`**: Cards with 50×50 fighter images, name and type, health and attack. POST **Heal** button when health < 100. Click cards for detailed unit pages.
- [x] **3 — fights**: On `/unit/all`, select two distinct living fighters on opposite teams. POST **Simulate** to `/fight/simulate`. Alternating attackers deal `random.randint(0, attack_points)` damage (capped by remaining HP). Every turn is stored in an `AttackEvent` with attacker, defender, roll, actual damage, and both remaining health values. Fighter health and fight results persist in SQLite.
- [x] **4a — history**: Unit detail shows a card for every fight with its winner/draw and all saved turns.
- [x] **4b — stats**: Bottom of `/unit/all` shows number of fights and actual total damage caused/taken by Blue and Red across persisted events.

## Design decisions / important edge cases

- Fighters with **0 health must be healed** before they can fight.
- When both fighters have AttackPoints 0, the fight is a **draw** with two saved zero-damage turns so it cannot loop forever. All other fights also have a safety limit of 2,000 attacks (a rare draw when no one reaches 0 HP).
- A damage roll can be zero. Damage *actually inflicted* is `min(roll, defender.health)` so final HP cannot become negative. Stats use actual inflicted damage, not overkill.
- A Blue-vs-Red fight counts **one fight for each team**. Both teams therefore have the same fight count under the challenge's different-team rule.
- A fight permanently updates each fighter's health. The **Heal** button restores health to 100, not the existing fight history.
- Cross-team validation happens on both the selection form and the simulation service. Updates and history inserts are wrapped in a database transaction.
- Images are loaded from user-entered URLs. Use publicly accessible `https://` links for them to appear in the browser.
- Accepts trailing-slash and slash-free versions of the specified challenge URLs.

## How the code maps to Django

| File | Purpose |
|---|---|
| `manage.py` | Command-line entry point |
| `fortress/urls.py` | URLs and route names |
| `units/models.py` | Database entities: `Unit`, `Fight`, `AttackEvent` |
| `units/forms.py` | Django form validation |
| `units/views.py` | HTTP GET/POST handlers, healing, pages, statistics |
| `units/services.py` | Fight algorithm and attack event persistence |
| `units/templates/units/` | HTML pages |
| `units/static/units/style.css` | UI styling |
| `units/migrations/` | Database migrations; no `makemigrations` needed |
| `units/tests.py` | Unit, heal, simulation, edge-case, stats tests |

## Submit to GitHub

Repository: `https://github.com/hiritt/Pita-si-Pateu-DjangoChallenge-Easy`

If you already cloned it, place **the contents** of this extracted folder (including `manage.py`, `fortress`, `units`, `requirements.txt`, `.gitignore`) into your clone. Do not include the containing folder as another nested level. Then, inside the cloned repository:

```powershell
git add .
git commit -m "Implement Django easy challenge tasks 1-4"
git push -u origin main
```

If `git` is not recognized, install Git for Windows and restart PyCharm. If your remote uses a different branch or contains commits, inspect `git branch -a` and `git status` rather than force-pushing. To use your own name/email for a new Git installation, configure `git config --global user.name` and `git config --global user.email`.

## Testing

`python manage.py test` should automatically discover the Django tests. It uses a separate, temporary test database. For a quick demonstration: add a Blue and a Red fighter, set Blue attack to 50 and Red attack to 15, simulate, view histories, compare statistics, and heal damaged fighters.

## Development-only settings

`fortress/settings.py` enables `DEBUG` and includes a sample development secret key; **do not deploy this project publicly** without proper production settings, valid host configuration, and an environment-provided secret key.

## Competition note

This is a standalone Django implementation. It is **not verified against** the organizers' optional `imimali/coderun2026-starter` repository, which may use its own conventions. Check any additional competition submission, originality, demonstration, or deployment rules with the organizers.
