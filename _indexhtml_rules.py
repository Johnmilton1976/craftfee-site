#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Close the third URL-variant door: /path/index.html

Cloudflare Pages answers /path/index.html with a 307 to /path/. The destination
is right, the status code is not: 307 is temporary, so a crawler keeps the source
URL on its books and re-fetches it. That is how /path (no slash) accumulated 70
entries in wagwise's "Page with redirect" bucket before 11-07 pinned it to 301.

`_redirects` cannot express /*/index.html — Cloudflare only honours a splat at the
end of the pattern — so this writes one exact rule per real directory and one for
the root. Idempotent: re-running replaces the generated block instead of stacking
a second copy.

Usage:
  python _indexhtml_rules.py pet-care-site/public
  python _indexhtml_rules.py etsy-fee-site/public
"""
import io
import os
import sys

BEGIN = "# ---- /dir/index.html -> /dir/ (generated, do not hand-edit) ----"
END = "# ---- end generated block ----"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pub = sys.argv[1].rstrip("/\\")
    rp = os.path.join(pub, "_redirects")

    dirs = []
    for root, _d, files in os.walk(pub):
        if "index.html" not in files:
            continue
        rel = os.path.relpath(root, pub).replace(os.sep, "/")
        rel = "" if rel == "." else rel
        dirs.append(rel)
    dirs.sort(key=lambda x: (x.count("/"), x))

    lines = [BEGIN,
             "# 307 -> 301. Cloudflare's own normalisation is temporary, which keeps",
             "# the index.html form alive in a crawler's queue forever.",
             "/index.html / 301"]
    for d in dirs:
        if d:
            lines.append("/%s/index.html /%s/ 301" % (d, d))
    lines.append(END)

    old = io.open(rp, encoding="utf-8", newline="").read() if os.path.isfile(rp) else ""
    old = old.replace("\r\n", "\n")
    if BEGIN in old:
        head = old[:old.index(BEGIN)].rstrip("\n")
        tail = old[old.index(END) + len(END):].lstrip("\n")
        new = head + "\n\n" + "\n".join(lines) + ("\n\n" + tail if tail.strip() else "\n")
    else:
        new = old.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"

    io.open(rp, "w", encoding="utf-8", newline="\n").write(new)
    print("%s: %d directory rules + /index.html" % (rp, len(dirs) - (1 if "" in dirs else 0)))


if __name__ == "__main__":
    main()
