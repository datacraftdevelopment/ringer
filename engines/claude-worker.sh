#!/usr/bin/env bash

# Remove inherited Claude/Anthropic configuration before loading the dedicated
# subscription credential. compgen and unset are Bash builtins.
sanitize_claude_environment() {
    local variable

    while IFS= read -r variable; do
        case "$variable" in
            ANTHROPIC_*|CLAUDECODE|CLAUDE_CODE_*)
                unset -v "$variable"
                ;;
        esac
    done < <(compgen -v)
}

sanitize_claude_environment

# This file is deliberately referenced, never displayed.
source /Users/joe/.config/ringer/claude.env

# Retain only the credential that the shim is required to restore. A second
# scrub prevents the credential file from accidentally restoring overrides.
oauth_token=${CLAUDE_CODE_OAUTH_TOKEN-}
sanitize_claude_environment
export CLAUDE_CODE_OAUTH_TOKEN="$oauth_token"
unset -v oauth_token

python3 - "$@" <<'PY'
import json
import os
import signal
import subprocess
import sys


def sum_integer_fields(value):
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        return sum(sum_integer_fields(item) for item in value.values())
    if isinstance(value, list):
        return sum(sum_integer_fields(item) for item in value)
    return 0


try:
    process = subprocess.Popen(
        ["claude", *sys.argv[1:]],
        stdout=subprocess.PIPE,
        stderr=None,
    )
except OSError as error:
    print(f"claude-worker.sh: unable to execute claude: {error}", file=sys.stderr)
    print("tokens used: 0")
    raise SystemExit(127)

captured = bytearray()
assert process.stdout is not None
while True:
    chunk = process.stdout.read(65536)
    if not chunk:
        break
    captured.extend(chunk)
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()

return_code = process.wait()

token_total = 0
try:
    result = json.loads(bytes(captured))
    usage = result["usage"]
    if not isinstance(usage, dict):
        raise TypeError("usage is not an object")
    token_total = sum_integer_fields(usage)
except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
    token_total = 0

if captured and not captured.endswith(b"\n"):
    sys.stdout.buffer.write(b"\n")
sys.stdout.buffer.write(f"tokens used: {token_total}\n".encode("ascii"))
sys.stdout.buffer.flush()

if return_code < 0:
    terminating_signal = -return_code
    signal.signal(terminating_signal, signal.SIG_DFL)
    os.kill(os.getpid(), terminating_signal)

raise SystemExit(return_code)
PY
