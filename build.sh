#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
mkdir -p bin
if [ ! -x bin/stockfish ]; then
  curl -L "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar" -o /tmp/stockfish.tar
  tar -xf /tmp/stockfish.tar -C /tmp
  found=$(find /tmp -type f -name 'stockfish*' | head -n 1)
  cp "$found" bin/stockfish
  chmod +x bin/stockfish
fi
