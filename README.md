# Brad's Claude Code Marketplace

A collection of Claude Code plugins for code quality and developer productivity.

## Installation

### 1. Add the marketplace

```bash
/plugin marketplace add s2bomb/brads-marketplace
```

### 2. Install plugins

Install one or both quality check plugins:

```bash
# For Python projects
/plugin install python-quality-hooks@brads-marketplace

# For TypeScript/JavaScript projects
/plugin install typescript-quality-hooks@brads-marketplace
```

### 3. Restart Claude Code

After installation, restart Claude Code to activate the plugins.

## Available Plugins

### python-quality-hooks

Automated code quality checks for Python files.

**Features:**
- **ruff** - Fast linter with auto-fix
- **basedpyright** - Type checker
- **bandit** - Security scanner

[View plugin details](./plugins/python-quality-hooks/README.md)

### typescript-quality-hooks

Automated code quality checks for TypeScript/JavaScript files.

**Features:**
- **Prettier** - Code formatter with auto-fix
- **ESLint** - Linter with auto-fix
- **TypeScript** - Type checker

[View plugin details](./plugins/typescript-quality-hooks/README.md)

## Usage

Once installed, plugins run automatically when you edit or write files. Each plugin only checks its specific file types (.py for Python, .ts/.tsx/.js/.jsx for TypeScript).

## Contributing

Have a plugin to add? Open an issue or PR!

## License

MIT
