#!/usr/bin/env python3

import json
import sys

if len(sys.argv) < 2:
    print("Usage: build.py builds.json", file=sys.stderr)
    sys.exit(1)

with open(sys.argv[1], "r") as f:
    builds = json.load(f)

print("""#!/bin/bash

set -x -e -u -o pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: ./build.sh <build-name>" >&2
    exit 1
fi

TARGET=$1

west init -l .
west update -o=--depth=1 -n

mkdir -p artifacts
""")

for b in builds:
    if b.get("disabled", False):
        continue

    name = b["name"]
    board = b["board"]
    built = b["artifact_built_name"]
    final = b["artifact_final_name"]

    extra_params = " ".join(
        f'-D{param}="{" ".join(values)}"'
        for param, values in b.get("extra_params", {}).items()
    )

    print(f"""
if [ "$TARGET" = "{name}" ]; then
    echo "Building {name}..."

    west build -d build-{name} -b {board} app -- -DBOARD_ROOT=${{PWD}}/app {extra_params}

    cp build-{name}/{built} artifacts/{final}

    echo "Build complete: artifacts/{final}"
fi
""")
