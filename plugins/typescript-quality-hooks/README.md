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

## Changelog

### v1.1.0 (2025-11-04)
**Major improvements to signal-to-noise ratio:**
- **78% noise reduction:** Added `--skipLibCheck` to TypeScript checker - eliminated 76+ errors from node_modules type definitions
- **Grouped output:** TypeScript errors now grouped by pattern instead of listed individually (e.g., "6× at lines 31, 32, 56..." instead of 6 separate entries)
- **File-scoped filtering:** Only shows TypeScript errors in the file you edited (not imported dependencies)
- **Removed filename redundancy:** Cleaner output format

**Before:** 97 errors (91 from node_modules), all listed individually
**After:** 21 errors in your file only, grouped into ~10 patterns

### v1.0.1 (2025-10-31)
Initial marketplace release
