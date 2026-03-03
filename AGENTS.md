# Repository Guidelines

## Project Structure & Module Organization
KiroGate currently contains two implementations:
- `main.ts` + `lib/*.ts`: Deno/TypeScript modular gateway (current primary path).
- `main.py` + `kiro_gateway/*.py`: FastAPI/Python gateway used by Docker deployment.
- `docker-compose.yml`, `Dockerfile`, and `fly.toml`: deployment and runtime config.
- Root-level config includes `deno.json` (tasks/style), `requirements.txt` (Python deps), and `cspell.json`.

When adding features, keep business logic in `lib/` (TS) or `kiro_gateway/` (Python), and keep entrypoints (`main.ts`, `main.py`) focused on wiring.

## Build, Test, and Development Commands
- `deno task dev`: run TypeScript server with file watching.
- `deno task start`: run TypeScript server once.
- `deno task check`: static type check for `main.ts` and imports.
- `deno fmt --check && deno lint`: enforce Deno formatting/lint rules.
- `python main.py`: run FastAPI server locally (port `8000`).
- `python -m compileall main.py kiro_gateway`: quick Python syntax validation.
- `docker compose up --build`: run containerized Python deployment.

## Coding Style & Naming Conventions
- TypeScript: follow `deno fmt` defaults from `deno.json` (2-space indent, single quotes, 120 columns).
- Python: 4-space indent, PEP 8 naming (`snake_case` functions/modules, `PascalCase` classes).
- Prefer descriptive module names (`rateLimiter.ts`, `request_handler.py`) and avoid adding logic-heavy code to route/entry files.
- Use explicit types in TS for public interfaces and request/response conversion boundaries.

## Testing Guidelines
There is no dedicated `tests/` directory yet. For each non-trivial change:
- Run `deno task check`, `deno fmt --check`, and `deno lint` for TS changes.
- Run `python -m compileall main.py kiro_gateway` for Python changes.
- Smoke test key endpoints manually (e.g., `GET /health`, `POST /v1/chat/completions`).
- If you add test infrastructure, place tests under `tests/` and mirror module names (`test_auth.py`, `translator.test.ts`).

## Commit & Pull Request Guidelines
Recent history follows Conventional Commit style (`feat:`, `fix:`, `refactor:`). Keep using this format:
- Example: `fix: handle empty streaming chunks in OpenAI adapter`.

PRs should include:
- concise problem/solution summary,
- linked issue (if available),
- validation steps/commands run,
- screenshots for admin/dashboard UI changes,
- notes on env var or API behavior changes.
