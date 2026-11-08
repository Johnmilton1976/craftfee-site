#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild each page's FAQPage JSON-LD from the Q&A a reader can actually see.

Why this exists: 2026-11-08 audit found the two sets had drifted apart. Pages
carried a visible "Quick answers" block written by hand, and separately a
FAQPage block written for search, sharing only a couple of questions. On
/etsy-fees-canada/ the schema asked "How much do Etsy fees take from a 30 CAD
sale in Canada?" - a question that appears nowhere on the page. Google's
structured-data policy wants marked-up content visible to a human, so the page
was claiming a Q&A it never showed.

Fixing it the other way round (rewriting the visible block to match the schema)
would mean editing 100+ hand-written answers. Driving the schema from the page
means the two can never drift again: the visible block is the source of truth.

Usage:
  python _sync_faq_schema.py            # dry run, prints per-page counts
  python _sync_faq_schema.py --apply    # rewrite the JSON-LD blocks
"""
import json
import os
import re
import sys

FAQ_H2 = re.compile(
    r"<h2[^>]*>\s*((?:Quick answers|Questions people ask[^<]*)|FAQ)\s*</h2>", re.I)
H3_P = re.compile(r"<h3[^>]*>([\s\S]*?)</h3>\s*<p[^>]*>([\s\S]*?)</p>")
LDJSON = re.compile(r"(<script[^>]+application/ld\+json[^>]*>)([\s\S]*?)(</script>)", re.I)


def plain(fragment):
    import html as _h
    t = re.sub(r"<[^>]+>", " ", fragment)
    t = _h.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def visible_qas(doc):
    m = FAQ_H2.search(doc)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"<h2", doc[start:])
    block = doc[start:start + nxt.start()] if nxt else doc[start:]
    out = []
    for q, a in H3_P.findall(block):
        qt, at = plain(q), plain(a)
        if qt and at:
            out.append((qt, at))
    return out


def build(qas):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qas
        ],
    }


def sync(doc, qas):
    """Return (new_doc, changed) with the FAQPage block replaced if needed."""
    target = json.dumps(build(qas), ensure_ascii=False, separators=(",", ":"))

    def repl(m):
        try:
            data = json.loads(m.group(2).strip())
        except Exception:
            return m.group(0)
        if not (isinstance(data, dict) and data.get("@type") == "FAQPage"):
            return m.group(0)
        repl.hit = True
        repl.old_n = len(data.get("mainEntity") or [])
        return m.group(1) + target + m.group(3)

    repl.hit = False
    repl.old_n = 0
    out = LDJSON.sub(repl, doc)
    return out, repl.hit, repl.old_n


def main(apply_change):
    total_changed = 0
    for root, dirs, files in os.walk("public"):
        for f in sorted(files):
            if f != "index.html":
                continue
            path = os.path.join(root, f)
            # newline="" on both read and write keeps the file's own line endings.
            # Without it Python converts CRLF to LF on read, writes LF back, and
            # every run leaves 16 files showing as modified with an empty diff.
            doc = open(path, encoding="utf-8", newline="").read()
            if '"FAQPage"' not in doc:
                continue
            qas = visible_qas(doc)
            rel = "/" + os.path.relpath(root, "public").replace("\\", "/") + "/"
            if not qas:
                print("%-42s 无可见问答区块，跳过" % rel)
                continue
            new, hit, old_n = sync(doc, qas)
            if not hit:
                print("%-42s 有可见问答 %d 条，但没找到 FAQPage 块" % (rel, len(qas)))
                continue
            state = "改" if new != doc else "已一致"
            print("%-42s 可见 %2d 条 | schema 原 %2d 条 -> %2d 条  %s"
                  % (rel, len(qas), old_n, len(qas), state))
            if new != doc:
                total_changed += 1
                if apply_change:
                    open(path, "w", encoding="utf-8", newline="").write(new)
    print("\n%s：%d 页需要更新" % ("已应用" if apply_change else "试运行", total_changed))
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
