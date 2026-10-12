#!/usr/bin/env sh
# Etsy Seller Tools - local preview (Git Bash / macOS / Linux)
# Usage:  sh start-preview.sh
# Stop:   press Ctrl+C

cd "$(dirname "$0")" || exit 1
PORT=8787

if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi

# If the port is taken (an old preview is still running), pick the next free one.
PORT=$($PY -c "
import socket
p=$PORT
while True:
    s=socket.socket()
    try:
        s.bind(('127.0.0.1',p)); s.close(); break
    except OSError:
        p+=1
print(p)
")

echo ""
echo "  ============================================"
echo "   Local preview :  http://127.0.0.1:$PORT/"
echo "   Stop          :  press Ctrl+C"
echo "  ============================================"
echo ""

command -v open >/dev/null 2>&1 && open "http://127.0.0.1:$PORT/"
command -v xdg-open >/dev/null 2>&1 && xdg-open "http://127.0.0.1:$PORT/"

exec $PY -m http.server "$PORT" --bind 127.0.0.1
