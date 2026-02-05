Hoe met Poetry de .toml te installeren:
- Met TortoiseGit, zet de git lokaal op je computer.
- Maak in Miniforge een nieuwe environment aan (open miniforge, typ: mamba create -n naam_van_je_nieuwe_environment python=3.13)
- typ: mamba activate naam_van_je_nieuwe_environment
- typ: python -m pip install --upgrade pip
  typ: pip install poetry
- typ: cd /path/to/your/project (path van het project waar map waar de .toml in staat)
  typ: poetry install
