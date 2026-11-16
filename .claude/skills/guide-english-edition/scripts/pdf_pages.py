#!/usr/bin/env python3
"""手順書 PDF のページ構成を点検する（Ghostscript で文字抽出・描画）。

使い方:
  python3 pdf_pages.py <guide_en.pdf> [--ref <guide.pdf>] [--render DIR] [--dpi 40]

検査内容:
  - ページ数（--ref があれば原文 PDF との差を報告）
  - 本文がほとんどないページ（目次のはみ出し、画像だけのページ、白紙ページ）
  - ページ末尾に取り残された見出し
  - PDF の更新日時が .md より古くないか（--md <guide_en.md> を渡したとき）
--render DIR を付けると全ページを PNG にして DIR に置く（目視確認用）。
ページの見た目（画像の切れ・はみ出し）は PNG を見て判断する。スクリプトは判定の補助。
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FOOTER = re.compile(r"^\d+\s*/\s*\d+$")
HEADING = re.compile(r"^(\d+(\.\d+)*\.?\s+\S|Appendix\b)")
THIN = 100  # 本文がこの文字数未満のページは「ほぼ空」とみなす（目次のはみ出しも拾える値）


def need_gs():
    if not shutil.which("gs"):
        print("[NG] Ghostscript（gs）が見つからない")
        sys.exit(1)


def page_texts(pdf):
    d = Path(tempfile.mkdtemp(prefix="pdfpages-"))
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=txtwrite",
                    f"-sOutputFile={d}/p%03d.txt", str(pdf)], check=True)
    pages = []
    for f in sorted(d.glob("p*.txt")):
        lines = [re.sub(r"\s+", " ", l).strip()
                 for l in f.read_text(encoding="utf-8", errors="replace").splitlines()]
        pages.append([l for l in lines if l])
    shutil.rmtree(d, ignore_errors=True)
    return pages


def strip_chrome(pages):
    """ヘッダ（全ページ共通の先頭行）とフッタ（n / N）を除いた本文行にする。"""
    heads = [p[0] for p in pages if p]
    common = max(set(heads), key=heads.count) if heads else None
    body = []
    for p in pages:
        b = [l for l in p if l != common and not FOOTER.match(l)]
        body.append(b)
    return body


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        print(__doc__)
        sys.exit(2)
    pdf = Path(a[0])
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    ref, render, md = opt("--ref"), opt("--render"), opt("--md")
    dpi = opt("--dpi") or "40"
    need_gs()
    failed = False

    body = strip_chrome(page_texts(pdf))
    n = len(body)
    print(f"[OK] ページ数: {n}")
    if ref:
        nref = len(page_texts(Path(ref)))
        print(f"[INFO] 原文 PDF は {nref} ページ（差 {n - nref:+d}）")

    if md:
        newer = Path(md).stat().st_mtime > pdf.stat().st_mtime
        if newer:
            print("[NG] PDF が .md より古い。PDF を再生成してから確認する")
            failed = True
        else:
            print("[OK] PDF は .md より新しい")

    thin = [(i + 1, sum(len(l) for l in b), b[0][:30] if b else "(白紙)")
            for i, b in enumerate(body) if sum(len(l) for l in b) < THIN]
    if thin:
        print(f"[WARN] 本文がほとんどないページ（{THIN} 文字未満）。画像だけのページは問題ない:")
        for no, chars, head in thin:
            print(f"   p.{no}: {chars} 文字 | {head}")
    else:
        print("[OK] 本文がほとんどないページはない")

    def is_toc(b):  # 見出し風の行が大半のページは目次なので除外する
        return sum(1 for l in b if HEADING.match(l)) >= len(b) / 2

    orphan = [i + 1 for i, b in enumerate(body[:-1])
              if b and HEADING.match(b[-1]) and not is_toc(b)]
    if orphan:
        print(f"[WARN] 見出しがページ末尾に取り残されている可能性: p.{orphan}")
    else:
        print("[OK] ページ末尾に取り残された見出しなし")

    if render:
        out = Path(render)
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m", f"-r{dpi}",
                        f"-sOutputFile={out}/p-%02d.png", str(pdf)], check=True)
        print(f"[OK] {len(list(out.glob('p-*.png')))} ページを {out} に描画した（目視確認用）")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
