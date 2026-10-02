#!/usr/bin/env bash
# Entry point without PowerShell. Forward arguments unchanged from any working directory.
set -euo pipefail
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ -n "${PYTHON:-}" ]]; then
    python_command="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
    python_command=python3
elif command -v python >/dev/null 2>&1; then
    python_command=python
else
    printf '%s\n' 'Python 3.10 or later is required. Install python3.' >&2
    exit 127
fi
if ! "$python_command" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    printf '%s\n' 'Specify Python 3.10 or later. PYTHON may contain the interpreter executable path.' >&2
    exit 1
fi
exec "$python_command" -X utf8 "$SCRIPT_DIR/initialize_optional_skills.py" "$@"
