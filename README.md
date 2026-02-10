Hoe met Poetry de .toml te installeren (tweede deel alleen HKV):
- Stap 1: met TortoiseGit, zet de checkout lokaal op je computer
- Stap 2 (HKV): Miniforge nieuwe environment aanmaken
    - Open miniforge, typ: mamba create -n naam_van_je_nieuwe_environment python=3.13
    - mamba activate naam_van_je_nieuwe_environment
    - python -m pip install --upgrade pip
    -  pip install poetry
- Stap 3: env installeren:
    - typ: cd /path/to/your/project (path van het project waar map waar de .toml in staat)
    - typ: poetry install
test test2