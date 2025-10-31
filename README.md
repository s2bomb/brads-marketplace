# Brad's Claude Code Marketplace

A collection of Claude Code plugins for code quality and developer productivity.

## Installation

### 1. Add the marketplace

```bash
/plugin marketplace add s2bomb/brads-marketplace
```

### 2. Install plugins

```bash
/plugin install code-quality-hooks@brads-marketplace
```

### 3. Restart Claude Code

After installation, restart Claude Code to activate the plugins.

## Available Plugins

### code-quality-hooks

Automated code quality checks for Python and TypeScript/JavaScript files.

**Features:**
- Python: ruff, basedpyright, bandit
- TypeScript/JS: prettier, eslint, tsc
- Auto-fixes issues when possible
- Only reports what needs manual fixing

[View plugin details](./plugins/code-quality-hooks/README.md)

## Usage

Once installed, plugins run automatically. For code-quality-hooks, quality checks trigger when you edit or write files.

## Contributing

Have a plugin to add? Open an issue or PR!

## License

MIT
