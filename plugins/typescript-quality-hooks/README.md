# TypeScript Quality Hooks

Automated code quality checks for TypeScript and JavaScript files that run automatically when you edit or write code in Claude Code.

## What it does

Runs quality checks after you edit or write TypeScript/JavaScript files (.ts, .tsx, .js, .jsx):

- **Prettier** - Code formatter with auto-fix
- **ESLint** - Linter with auto-fix, shows grouped rule violations
- **TypeScript** - Type checker with detailed errors

## Requirements

```bash
# Tools should be in your project's node_modules
npm install --save-dev prettier eslint typescript
```

## How it works

- Triggers automatically on Edit/Write operations for .ts, .tsx, .js, .jsx files
- Auto-fix runs first (prettier, eslint)
- Only reports issues that need manual fixing
- Silent if all checks pass
- Shows concise, actionable feedback

## Configuration

Uses your project's existing configuration files:
- `.prettierrc` for Prettier
- `.eslintrc.*` for ESLint
- `tsconfig.json` for TypeScript

## Timeout

Hook has a 30-second timeout. If checks take longer, they'll be terminated.
