#!/usr/bin/env sh
# 兼容旧命令入口：转发给跨平台 Python 版 archival_search.py
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/archival_search.py" "$@"
