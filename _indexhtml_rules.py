#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Close the URL-variant doors in _redirects — both of them, generated.

Cloudflare Pages answers /path (no slash) and /path/index.html with a 307 to
/path/. The destination is right, the status code is not: 307 is temporary, so a
crawler keeps the source URL on its books and re-fetches it. That is how
/path (no slash) accumulated 70 entries in wagwise's "Page with redirect" bucket
before 11-07, and how /etsy-fee-history and /sitemap were still answering 307 on
craftfee in 11-08 — their no-slash lines had simply been forgotten by hand.

`_redirects` cannot express /*/index.html — Cloudflare only honours a splat at
the end of the pattern — and a bare /* would also match trailing-slash requests
and loop. So every rule is one exact line per real directory, generated from the
filesystem. Two generated blocks, both idempotent:

    # ---- /dir -> /dir/ (generated, do not hand-edit) ----
    # ---- /dir/index.html -> /dir/ (generated, do not hand-edit) ----

Hand-written rules (historical aliases like /etsy-offsite-ads/ -> /offsite-ads/)
stay above the generated blocks and are never touched. Adding a page now only
means running this script; forgetting a line is no longer possible.

Usage:
  python _indexhtml_rules.py pet-care-site/public
  python _indexhtml_rules.py etsy-fee-site/public
"""
import io
import os
import re
import sys

BEGIN_NO = "# ---- /dir -> /dir/ (generated, do not hand-edit) ----"
BEGIN = "# ---- /dir/index.html -> /dir/ (generated, do not hand-edit) ----"
END = "# ---- end generated block ----"

# 手写的「同一路径去掉斜杠」规则：生成块已经覆盖，留着会变成重复定义。
DUP_NOSLASH = re.compile(r"^/([^\s/]+(?:/[^\s/]+)*) /\1/ 301$")


def replace_block(text, begin, lines):
    """用新的 lines 替换 begin..END 之间的内容；没有该块就追加到末尾。"""
    if begin in text:
        head = text[:text.index(begin)].rstrip("\n")
        after = text[text.index(begin):]
        tail = after[after.index(END) + len(END):].lstrip("\n")
        return head + "\n\n" + "\n".join(lines) + ("\n\n" + tail if tail.strip() else "\n")
    return text.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"


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

    no_slash = [BEGIN_NO,
                "# 平台默认 307（临时），会把这个变体长期留在抓取队列里，",
                "# 这就是 GSC「网页会自动重定向」的来源。不能用 /*（会匹配带斜杠请求 -> 死循环）。"]
    for d in dirs:
        if d:
            no_slash.append("/%s /%s/ 301" % (d, d))
    no_slash.append(END)

    idx = [BEGIN,
           "# 307 -> 301. Cloudflare's own normalisation is temporary, which keeps",
           "# the index.html form alive in a crawler's queue forever.",
           "/index.html / 301"]
    for d in dirs:
        if d:
            idx.append("/%s/index.html /%s/ 301" % (d, d))
    idx.append(END)

    old = io.open(rp, encoding="utf-8", newline="").read() if os.path.isfile(rp) else ""
    old = old.replace("\r\n", "\n")

    # 先摘掉手写的同路径斜杠规则（生成块接管），只保留 src != dst 的历史别名
    kept, dropped = [], 0
    for line in old.split("\n"):
        if DUP_NOSLASH.match(line.strip()):
            dropped += 1
            continue
        kept.append(line)
    old = "\n".join(kept)

    new = replace_block(old, BEGIN_NO, no_slash)
    new = replace_block(new, BEGIN, idx)

    io.open(rp, "w", encoding="utf-8", newline="\n").write(new)
    subdirs = len([d for d in dirs if d])
    print("%s: %d 个目录 -> %d 条无斜杠 301 + %d 条 index.html 301（摘掉手写重复 %d 条）"
          % (rp, subdirs, subdirs, subdirs, dropped))


if __name__ == "__main__":
    main()
