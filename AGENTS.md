# Repository Guidelines

## Project Structure & Module Organization
The core application lives in `src/`, with `main.py` providing the Typer CLI, `metrics.py` hosting the analytics functions, and `dashboard.py` powering the Streamlit UI. Shared configuration and data helpers sit in `config.py` and `data.py`. Generated artifacts land in `data/production.json`, while automated checks reside under `tests/`. Interactive dashboards start from `run_dashboard.py`, and documentation lives at the repository root alongside installation plans.

## Build, Test, and Development Commands
- `python -m src.main setup` – generate the 30-day factory dataset in `data/`.
- `python -m src.main chat` – launch the text chatbot for manual verification.
- `python -m src.main voice` – exercise the Whisper/TTS flow (requires `OPENAI_API_KEY`).
- `python run_dashboard.py` – open the Streamlit dashboard locally.
- `pytest` – execute the unit and smoke tests.

## Coding Style & Naming Conventions
Target Python 3.11 with 4-space indentation and type-aware docstrings where logic is non-trivial. Follow snake_case for functions, lower_snake_case for module-level variables, and PascalCase for Typer command classes (if introduced). Format Python files with `black .` before pushing; keep imports standard-library → third-party → local. Keep Streamlit layout definitions declarative and isolate tool-specific constants inside `config.py`.

## Testing Guidelines
Use `pytest` from the project root; tests assume the generated dataset exists, so run the setup command first or mock data paths. Add new tests in `tests/` mirroring the module under test (`test_<module>.py`). For coverage checks, run `pytest --cov=src --cov-report=html` and review `htmlcov/index.html` before submission. Favor deterministic fixtures over on-the-fly random generation so chatbot behaviours remain reproducible.

## Commit & Pull Request Guidelines
Write commit subjects in imperative mood (e.g., `Add downtime visualization tweak`) and limit them to ~60 characters with concise bodies when needed. Every pull request should summarize user-facing changes, list validation steps (commands run, datasets updated), and reference related issues or plans (e.g., `implementation-plan.md`). Attach screenshots or terminal snippets for dashboard or voice updates, and call out any required configuration changes to `.env` or Azure resources.

## Security & Configuration Tips
Never commit `.env` or credential-bearing files; rely on `.env.example` to document expected variables (`AZURE_ENDPOINT`, `AZURE_API_KEY`, etc.). Rotate keys used for demos and prefer environment-specific overrides via shell exports when screen-recording. Validate external dependencies against `requirements.txt` and pin any new additions to maintain reproducible deployments.
