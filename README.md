Hoe met Poetry de .toml te installeren (tweede deel alleen HKV):
- Stap 1: met TortoiseGit, zet de checkout lokaal op je computer
- Stap 2 (HKV): met `pipx` de package manager `poetry` installeren.
    - installeer `pipx` met het commando `pip install pipx; pipx ensurepath`
    - installeer `poetry` met het commando `pipx install poetry<2.0`
- Stap 3: env installeren:
    - typ: `cd /path/to/your/project` (path van het project waar map waar de .toml in staat)
    - typ: `poetry install`
