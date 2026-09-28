#!/usr/bin/env sh
set -eu
SITE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SITE_PORT=${1:-4186}
if [ ! -x "$SITE_ROOT/.venv/bin/python" ]; then
    printf '缺少本地 Jupyter 环境。请先按 README 的安装步骤准备环境。\n' >&2
    exit 1
fi
if [ ! -f "$SITE_ROOT/.runtime/jupyter-data/kernels/julia-1806/kernel.json" ]; then
    printf '缺少 Julia 内核。请先运行 scripts/install-julia-packages.sh。\n' >&2
    exit 1
fi
printf '18.06 学习室：http://127.0.0.1:%s/learn/\n首次访问请使用下面 Jupyter 提供的登录链接。按 Ctrl+C 停止。\n' "$SITE_PORT"
"$SITE_ROOT/.venv/bin/python" "$SITE_ROOT/scripts/generate_content.py"
exec "$SITE_ROOT/.venv/bin/python" "$SITE_ROOT/scripts/serve.py" --port "$SITE_PORT"
