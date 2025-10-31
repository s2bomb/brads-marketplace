# Code Quality Hooks

Automated code quality checks for Python and TypeScript/JavaScript files that run automatically when you edit or write code in Claude Code.

## What it does

This plugin installs hooks that run quality checks after you edit or write files:

### Python files (.py)
- **ruff** - Fast Python linter with auto-fix
- **basedpyright** - Type checker showing full error details
- **bandit** - Security vulnerability scanner

### TypeScript/JavaScript files (.ts, .tsx, .js, .jsx)
- **Prettier** - Code formatter with auto-fix
- **ESLint** - Linter with auto-fix, shows grouped rule violations
- **TypeScript** - Type checker with detailed errors

## Requirements

### Python projects
```bash
# Install with uv (recommended)
uv pip install ruff basedpyright bandit
```

### TypeScript/JavaScript projects
```bash
# Tools should be in your project's node_modules
npm install --save-dev prettier eslint typescript
```

## How it works

- Hooks trigger automatically on Edit/Write operations
- Auto-fix runs first (ruff, prettier, eslint)
- Only reports issues that need manual fixing
- Silent if all checks pass
- Shows concise, actionable feedback

## Configuration

The hooks use your project's existing configuration files:
- `ruff.toml` or `pyproject.toml` for ruff
- `.prettierrc` for Prettier
- `.eslintrc.*` for ESLint
- `tsconfig.json` for TypeScript

## Timeout

Each hook has a 30-second timeout. If checks take longer, they'll be terminated.
