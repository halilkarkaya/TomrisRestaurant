#!/usr/bin/env bash
# Eski komutlarla uyumluluk icin update.sh betigine yonlendirir.
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec bash "$SCRIPT_DIR/update.sh" "$@"
