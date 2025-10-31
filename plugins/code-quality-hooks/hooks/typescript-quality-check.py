#!/usr/bin/env python3
"""
TypeScript/JavaScript Quality Check Hook for Claude Code
Runs Prettier, ESLint, and TypeScript type checking on edited files.
Only reports issues that require manual fixing.

Matches Python hook philosophy:
- Find, don't frontload (progressive disclosure)
- Silent if clean
- Auto-fix first, report what remains
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def run_command(cmd: list[str], cwd: str | None = None) -> tuple[str, int]:
    """Run a command and return (output, exit_code)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(cmd)}", 1
    except Exception as e:
        return f"Error running {' '.join(cmd)}: {e}", 1


def parse_prettier_output(output: str, exit_code: int) -> str | None:
    """
    Parse Prettier output and return Level 2 formatted message.

    Level 2: Show file, line:col, error message (no code context)

    Exit codes:
        0 = Clean or successfully formatted (return None - silent)
        1 = Needs formatting (shouldn't happen with --write)
        2 = Syntax error (return formatted error)
    """
    # Exit 0: Clean or fixed - silent
    if exit_code == 0:
        return None

    # Exit 1: Needs formatting (shouldn't happen if --write ran)
    if exit_code == 1:
        # Check if file listed in warnings
        warn_match = re.search(r"\[warn\] (.+)$", output, re.MULTILINE)
        if warn_match:
            filename = warn_match.group(1).strip()
            # Extract just filename from path
            filename = filename.split("/")[-1]
            return f"Prettier: Formatting needed in {filename} (--write failed?)"
        return "Prettier: Formatting issues detected"

    # Exit 2: Syntax error - parse and format
    if exit_code == 2:
        # Pattern: [error] path/to/file.ts: ErrorType: message (line:col)
        error_pattern = r"\[error\] ([^:]+): (\w+): (.+?) \((\d+):(\d+)\)"
        match = re.search(error_pattern, output)

        if match:
            filepath = match.group(1).strip()
            error_type = match.group(2).strip()
            error_msg = match.group(3).strip()
            line = match.group(4)
            col = match.group(5)

            # Extract just the filename from path
            filename = filepath.split("/")[-1]

            return (
                f"Prettier: Syntax error at {filename}:{line}:{col}\n"
                f"  {error_type}: {error_msg}"
            )

        # Fallback if pattern doesn't match
        if "[error]" in output:
            # Try to extract filename at least
            file_match = re.search(r"\[error\] ([^\s:]+)", output)
            if file_match:
                filename = file_match.group(1).split("/")[-1]
                return f"Prettier: Syntax error in {filename}"
            return "Prettier: Syntax error detected"

    # Unknown exit code
    return f"Prettier: Unexpected exit code {exit_code}"


def check_prettier(file_path: str, project_root: Path) -> str | None:
    """Run Prettier --write (auto-fix). Returns Level 2 message if issues remain."""
    rel_path = Path(file_path).relative_to(project_root)

    # Auto-fix with --write (use npx to find prettier in monorepo)
    output, exit_code = run_command(
        ["npx", "prettier", "--write", str(rel_path)], cwd=str(project_root)
    )

    # Use Level 2 parser
    return parse_prettier_output(output, exit_code)


def parse_eslint_output(output: str) -> str | None:
    """
    Parse ESLint output and return Level 2 formatted message.

    Level 2: Grouped by rule with counts + line numbers
    """
    # Check if output is empty or clean
    if not output or not output.strip():
        return None

    # Check for "no problems" indicator
    if "✖ 0 problems" in output:
        return None

    # Parse the summary line: ✖ X problems (Y errors, Z warnings)
    summary_pattern = r"✖ (\d+) problems? \((\d+) errors?, (\d+) warnings?\)"
    summary_match = re.search(summary_pattern, output)

    if not summary_match:
        return None

    total = int(summary_match.group(1))
    errors = int(summary_match.group(2))
    warnings = int(summary_match.group(3))

    if total == 0:
        return None

    # Extract filename from first non-empty line
    filename = None
    for line in output.split("\n"):
        if line.strip() and not line.startswith(" "):
            filename = line.strip().split("/")[-1]
            break

    # Parse each issue line
    # Format:   line:col  level  message  rule-name
    issue_pattern = r"^\s+(\d+):(\d+)\s+(warning|error)\s+(.+?)\s+([\w@/-]+)\s*$"

    issues_by_rule = defaultdict(list)

    for line in output.split("\n"):
        match = re.match(issue_pattern, line)
        if match:
            line_num = match.group(1)
            rule = match.group(5)
            issues_by_rule[rule].append(line_num)

    if not issues_by_rule:
        # Have summary but no parsed issues - just return count
        if errors > 0 and warnings > 0:
            return f"ESLint: {errors} error(s), {warnings} warning(s)"
        elif errors > 0:
            return f"ESLint: {errors} error(s)"
        else:
            return f"ESLint: {warnings} warning(s)"

    # Format Level 2 output
    result_lines = []

    # Header with filename if available
    if filename:
        if errors > 0 and warnings > 0:
            result_lines.append(
                f"ESLint: {errors} error(s), {warnings} warning(s) in {filename}"
            )
        elif errors > 0:
            result_lines.append(f"ESLint: {errors} error(s) in {filename}")
        else:
            result_lines.append(f"ESLint: {warnings} warning(s) in {filename}")
    else:
        if errors > 0 and warnings > 0:
            result_lines.append(f"ESLint: {errors} error(s), {warnings} warning(s)")
        elif errors > 0:
            result_lines.append(f"ESLint: {errors} error(s)")
        else:
            result_lines.append(f"ESLint: {warnings} warning(s)")

    # Group issues by rule
    for rule, lines in sorted(issues_by_rule.items(), key=lambda x: -len(x[1])):
        count = len(lines)
        lines_str = ", ".join(lines)
        result_lines.append(f"  - {rule}: {count}× (lines {lines_str})")

    return "\n".join(result_lines)


def check_eslint(file_path: str, project_root: Path) -> str | None:
    """Run ESLint --fix, then check remaining. Returns Level 2 formatted output."""
    rel_path = Path(file_path).relative_to(project_root)

    # Auto-fix first
    run_command(["npx", "eslint", "--fix", str(rel_path)], cwd=str(project_root))

    # Check what remains
    output, _ = run_command(["npx", "eslint", str(rel_path)], cwd=str(project_root))

    # Use Level 2 parser
    return parse_eslint_output(output)


def parse_typescript_output(output: str, exit_code: int) -> str | None:
    """
    Parse TypeScript output and return Level 1 formatted message.

    Level 1 (Full): Shows every error with complete details
    """
    # Exit 0 or empty output = clean
    if exit_code == 0 or not output or not output.strip():
        return None

    # Parse each error line
    # Format: path/to/file.ts(line,col): error TSXXXX: Error message.
    error_pattern = r"^(.+)\((\d+),(\d+)\): error (TS\d+): (.+)$"

    errors = []
    filename = None

    for line in output.split("\n"):
        match = re.match(error_pattern, line.strip())
        if match:
            filepath = match.group(1).strip()
            line_num = match.group(2)
            col_num = match.group(3)
            error_code = match.group(4)
            error_msg = match.group(5).strip()

            # Extract just filename from path
            if not filename:
                filename = filepath.split("/")[-1]

            errors.append({
                "filename": filepath.split("/")[-1],
                "line": line_num,
                "col": col_num,
                "code": error_code,
                "message": error_msg,
            })

    if not errors:
        return None

    # Format Level 1 output
    result_lines = []

    # Header with count and filename
    error_count = len(errors)
    if filename:
        result_lines.append(f"TypeScript: {error_count} error(s) in {filename}")
    else:
        result_lines.append(f"TypeScript: {error_count} error(s)")

    # List each error with full details
    for error in errors:
        result_lines.append(
            f"  - {error['filename']}({error['line']},{error['col']}): "
            f"{error['code']}: {error['message']}"
        )

    return "\n".join(result_lines)


def check_typescript(file_path: str, project_root: Path) -> str | None:
    """Run tsc --noEmit. Returns Level 1 formatted output."""
    rel_path = Path(file_path).relative_to(project_root)

    output, exit_code = run_command(
        ["npx", "tsc", "--noEmit", str(rel_path)],
        cwd=str(project_root),
    )

    # Use Level 1 parser
    return parse_typescript_output(output, exit_code)


def main() -> None:
    """Hook entry point."""
    # Read hook input
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Get file path from tool input
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only process TypeScript/JavaScript files
    if not file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        sys.exit(0)

    # Verify file exists
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        sys.exit(0)

    # Find project root (where node_modules is)
    project_root = file_path_obj.parent
    while project_root != project_root.parent:
        if (project_root / "node_modules").exists():
            break
        project_root = project_root.parent
    else:
        # No node_modules found, skip
        sys.exit(0)

    # Run quality checks
    issues: list[str] = []

    prettier_msg = check_prettier(file_path, project_root)
    if prettier_msg:
        issues.append(prettier_msg)

    eslint_msg = check_eslint(file_path, project_root)
    if eslint_msg:
        issues.append(eslint_msg)

    typescript_msg = check_typescript(file_path, project_root)
    if typescript_msg:
        issues.append(typescript_msg)

    # If no issues, exit silently
    if not issues:
        sys.exit(0)

    # Report issues to Claude via additionalContext
    context_message = (
        f"Code quality for {file_path_obj.name}:\n"
        + "\n".join(f"- {issue}" for issue in issues)
    )

    output: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context_message,
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
