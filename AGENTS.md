# Repository Guidelines

## Project Structure & Module Organization
Core code sits in `src/`: `main.py` exposes the Typer CLI, `metrics.py` powers analytics, and `dashboard.py` renders the Streamlit UI. Config, data, and models live in `config.py`, `data.py`, `models.py`. Data persists in `data/production.json`, tests stay under `tests/`, and `run_dashboard.py` launches the dashboard. React + TypeScript work should live in a sibling `frontend/` folder that uses the shared API layer.

## Build, Test, and Development Commands
Key commands: `python -m src.main setup` (generate data), `python -m src.main chat` (chatbot), `python -m src.main voice` (voice, speech keys required), `python run_dashboard.py` (dashboard), and `pytest` (unit + smoke tests).

## Coding Style, Tooling & Naming
Follow `.claude/CLAUDE.md`: Python-first, synchronous by default. Use 4-space indentation, snake_case for functions and module variables, PascalCase for classes, and import order standard library → third party → local. Run `black` (line length 88), rely on Pydantic/SQLModel for validation, keep Streamlit pages declarative, and use Rich sparingly. React features should lean on TypeScript plus Material-UI, Recharts, and MSAL helpers.

## Testing Guidelines
Run `pytest` from the root after generating data or supplying fixtures. Mirror modules with `tests/test_<module>.py`, keep fixtures stable, and use `pytest --cov=src --cov-report=html` when coverage matters. Reach for async test clients only when FastAPI endpoints truly demand them.

## Commit & Pull Request Guidelines
Write imperative commit subjects (≤60 characters) and add detail only when needed. Pull requests should explain the change, list validation steps, link to plans or issues, and include screenshots when visuals shift. Flag `.env` or Azure configuration edits so setups stay reproducible.

## Development Preferences Snapshot
CLAUDE defaults apply:
- FastAPI for APIs, React + TypeScript (Material-UI, Recharts) for dashboards, Typer + Rich for CLI UX
- Azure-first: Azure OpenAI, Blob Storage, Azure AD/MSAL, and Azure Container Apps/App Service
- SQLModel or Tortoise for durable storage; JSON/SQLite or Blob JSON for prototypes
- Dramatiq/Celery only when workloads demand it; ship Docker images and Vite builds when deploying

## Security & Configuration Tips
Keep secrets out of version control; update `.env.example` when Azure endpoints, keys, or storage strings change. Rotate demo keys, prefer environment overrides when recording, add defensive error handling, and lean on Key Vault or managed identities in Azure.

## Prototype Defaults
For demos and spikes, favor synchronous I/O, manual smoke tests, consolidated modules, and minimal dependencies. Note shortcuts in PR descriptions so future contributors can harden them later.
