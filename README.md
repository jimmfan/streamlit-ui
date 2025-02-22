# Instructions for setting up UV virtual env
uv venv .venv
uv pip install .
source .venv/bin/activate
mkdir -p .vscode && touch .vscode/settings.json

# .vscode/settings.json
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.analysis.extraPaths": [".venv/lib/python3.13.1/site-packages"]
}
```
