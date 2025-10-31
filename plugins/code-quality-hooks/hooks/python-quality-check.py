#!/usr/bin/env python3
"""
Python Quality Check Hook for Claude Code
Runs ruff, basedpyright, and bandit on edited Python files.
Only reports issues that require manual fixing.
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[str, int]:
    """Run a command and return (output, exit_code)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(cmd)}", 1
    except Exception as e:
        return f"Error running {' '.join(cmd)}: {e}", 1


def check_ruff(file_path: str) -> str | None:
    """Run ruff check with auto-fix. Returns message if issues remain."""
    output, _ = run_command(["uv", "run", "ruff", "check", "--fix", file_path])

    # Check for remaining issues
    if "0 remaining" in output or "All checks passed" in output:
        return None

    # Parse remaining issues
    if "remaining" in output:
        lines = output.strip().split('\n')
        # Find the summary line like "Found 3 errors (1 fixed, 2 remaining)"
        for line in lines:
            if "remaining" in line and "fixed" in line:
                return f"ruff: {line.strip()}"

    # If there are any errors shown, return them
    if output.strip() and "All checks passed" not in output:
        return f"ruff issues:\n{output.strip()}"

    return None


def check_basedpyright(file_path: str) -> str | None:
    """
    Run basedpyright with Level 2 parsing.
    Shows: Full error details + warning count only.
    """

    output, exit_code = run_command(["uv", "run", "basedpyright", file_path])
    lines = output.strip().split("\n")

    errors = []
    summary = None

    # Find summary line
    for line in reversed(lines):
        if " error" in line and " warning" in line:
            summary = line.strip()
            break

    if not summary:
        return None

    # Check if there are any issues
    if "0 error" in summary and "0 warning" in summary:
        return None

    # Parse errors only (skip warnings) - Level 2
    current_error_lines = []

    for line in lines:
        is_error = bool(re.match(r"\s+.+:\d+:\d+ - error:", line))
        is_warning = bool(re.match(r"\s+.+:\d+:\d+ - warning:", line))
        is_context = bool(re.match(r"\s{4,}[A-Z\"]", line.strip() and line))

        if is_error:
            # Save previous error if exists
            if current_error_lines:
                errors.append("\n".join(current_error_lines))
            # Start new error
            current_error_lines = [line]

        elif is_warning:
            # Save current error if exists, then stop tracking
            if current_error_lines:
                errors.append("\n".join(current_error_lines))
                current_error_lines = []

        elif is_context and current_error_lines:
            # Add context to current error
            current_error_lines.append(line)

        else:
            # Hit something else (blank line, summary, etc)
            if current_error_lines:
                errors.append("\n".join(current_error_lines))
                current_error_lines = []

    # Don't forget last error
    if current_error_lines:
        errors.append("\n".join(current_error_lines))

    # Format output
    if errors:
        return "\n".join(errors) + "\n" + summary

    # Only warnings, just show summary
    return summary


def check_bandit(file_path: str) -> str | None:
    """Run bandit security check. Returns message if issues found."""
    output, exit_code = run_command(["uv", "run", "bandit", "-q", file_path])

    # bandit exit codes: 0 = no issues, 1 = issues found
    if exit_code == 0 or not output.strip():
        return None

    # Parse severity counts from output
    lines = output.strip().split('\n')
    for line in lines:
        if "Total issues (by severity):" in line:
            idx = lines.index(line)
            # Get next few lines with severity counts
            severity_info = lines[idx:idx+5]
            # Filter for non-zero counts
            issues = []
            for sev_line in severity_info:
                if any(level in sev_line for level in ["Low:", "Medium:", "High:"]):
                    # Extract count
                    if not sev_line.strip().endswith(": 0"):
                        # Extract just the severity and count
                        parts = sev_line.strip().split(":")
                        if len(parts) == 2:
                            severity = parts[0].strip()
                            count = parts[1].strip()
                            issues.append(f"{severity}: {count}")

            if issues:
                return "bandit: " + ", ".join(issues)

    # If we can't parse, just report that issues exist
    if "Issue:" in output:
        return "bandit: Security issues detected"

    return None


def main():
    # Read hook input
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Get file path from tool input
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only process Python files
    if not file_path.endswith(".py"):
        sys.exit(0)

    # Verify file exists
    if not Path(file_path).exists():
        sys.exit(0)

    # Run quality checks
    issues = []

    ruff_msg = check_ruff(file_path)
    if ruff_msg:
        issues.append(ruff_msg)

    basedpyright_msg = check_basedpyright(file_path)
    if basedpyright_msg:
        issues.append(basedpyright_msg)

    bandit_msg = check_bandit(file_path)
    if bandit_msg:
        issues.append(bandit_msg)

    # If no issues, exit silently
    if not issues:
        sys.exit(0)

    # Report issues to Claude via additionalContext
    context_message = f"Code quality for {Path(file_path).name}:\n" + "\n".join(f"- {issue}" for issue in issues)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context_message
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
