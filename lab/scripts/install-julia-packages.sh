#!/usr/bin/env sh
set -eu
SITE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -z "${JULIA_BIN:-}" ]; then
    if [ -f "$SITE_ROOT/.runtime/julia-version.json" ]; then
        JULIA_VERSION=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$SITE_ROOT/.runtime/julia-version.json")
        JULIA_BIN="$SITE_ROOT/.runtime/julia-$JULIA_VERSION/bin/julia"
    else
        JULIA_BIN=$(command -v julia || true)
    fi
fi
if [ -z "$JULIA_BIN" ] || [ ! -x "$JULIA_BIN" ]; then
    printf '请先安装 Julia 1.12.5，或通过 JULIA_BIN 指定 Julia 可执行文件。\n' >&2
    exit 1
fi
export JULIA_DEPOT_PATH="$SITE_ROOT/.runtime/julia-depot"
export JUPYTER_DATA_DIR="$SITE_ROOT/.runtime/jupyter-data"
export JUPYTER="$SITE_ROOT/.venv/bin/jupyter"
export PYTHON="$SITE_ROOT/.venv/bin/python"
export JULIA_PKG_PRECOMPILE_AUTO=0
export JULIA_NUM_PRECOMPILE_TASKS=2
export IJULIA_NODEFAULTKERNEL=1
export MPLCONFIGDIR="$SITE_ROOT/.runtime/matplotlib"
export MPLBACKEND=Agg
export GKSwstype=100
exec "$JULIA_BIN" --project="$SITE_ROOT/julia" "$SITE_ROOT/scripts/setup_julia.jl" "$SITE_ROOT" "$@"
