# Python Quality Hooks

Automated code quality checks for Python files that run automatically when you edit or write code in Claude Code.

## What it does

Runs quality checks after you edit or write Python files (.py):

- **ruff** - Fast Python linter with auto-fix
- **basedpyright** - Type checker showing full error details
- **bandit** - Security vulnerability scanner

## Requirements

```bash
# Install with uv (recommended)
uv pip install ruff basedpyright bandit
```

## How it works

- Triggers automatically on Edit/Write operations for .py files
- Auto-fix runs first (ruff)
- Only reports issues that need manual fixing
- Silent if all checks pass
- Shows concise, actionable feedback

## Configuration

Uses your project's existing configuration files:
- `ruff.toml` or `pyproject.toml` for ruff
- `pyproject.toml` or `pyrightconfig.json` for basedpyright
- `.bandit` or `pyproject.toml` for bandit

## Timeout

Hook has a 30-second timeout. If checks take longer, they'll be terminated.
