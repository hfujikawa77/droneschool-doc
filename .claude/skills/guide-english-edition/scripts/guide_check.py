#!/usr/bin/env python3
"""手順書（Markdown）の英語版を作るための決定論処理。

使い方:
  # 目次（<!-- code_chunk_output --> ブロック）が見出しと一致するか検査する
  python3 guide_check.py toc-check <guide.md>
  # 見出しから目次を作り直す（英語版の見出し・アンカー更新に使う。改行コードは維持）
  python3 guide_check.py toc-write <guide_en.md>
  # 英語版の改行コードを原文（CRLF/LF）に揃える（Write で書いた直後に実行する）
  python3 guide_check.py eol-match <guide.md> <guide_en.md>
  # 原文と英語版を構造的に照合する
  python3 guide_check.py compare <guide.md> <guide_en.md>

compare の検査内容:
  [NG]   改行コードの不一致 / 見出しの数・階層・番号の不一致 / 改ページ位置の不一致
         表の行数の不一致 / コードブロック数の不一致、コマンド行（日本語を含まない行）の改変
         画像参照の数の不一致・実在しないファイル / 解決できない内部リンク（#anchor）
         目次と見出しの不一致 / 可視テキストの日本語・全角記号の残り
  [WARN] HTML コメント・コードブロック内の日本語の残り（改訂履歴コメントなど）
  [INFO] 原文と異なる画像参照・URL（意図した差し替えか確認する）
問題（NG）があれば終了コード 1。
"""
import re
import sys
from pathlib import Path

# ひらがな・カタカナ・漢字・CJK 記号。全角形は ＜＞（プレースホルダ用）を除いて別扱いにする。
CJK = re.compile(r"[　-ヿ一-鿿]")
FULLWIDTH = re.compile(r"[＀-￯]")
KEEP_FULLWIDTH = "＜＞"
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE_LINE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
ANCHOR = re.compile(r"\]\(#([^)\s]+)\)")
URL = re.compile(r"https?://[^\s)>\"'`]+")
NUMBER = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")
TOC_BEGIN = "<!-- code_chunk_output -->"
TOC_END = "<!-- /code_chunk_output -->"
TOC_CMD = re.compile(r'<!--\s*@import\s+"\[TOC\]"\s*\{([^}]*)\}')


def slug(text, seen):
    """Markdown Preview Enhanced / GitHub 互換のアンカー。重複には -1, -2 を付ける。"""
    s = re.sub(r"[^\w\- ]", "", text.replace("\\&", "&").lower()).strip().replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


def blank_comments(text):
    """HTML コメントを空にする（行番号は維持）。"""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def parse(text):
    """見出し・改ページ・表・コードブロックなどを走査して返す。"""
    lines = blank_comments(text).splitlines()
    out = {"headings": [], "breaks": [], "tables": [], "fences": [], "visible": [],
           "images": [], "anchors": [], "urls": []}
    in_fence, fence, run = False, None, 0
    for line in lines:
        if FENCE_LINE.match(line):
            if in_fence:
                out["fences"].append(fence)
            else:
                fence = []
            in_fence = not in_fence
            continue
        if in_fence:
            fence.append(line)
            continue
        out["visible"].append(line)
        if "page-break-before" in line:
            out["breaks"].append(len(out["headings"]))  # 直前までの見出し数で位置を表す
        m = HEADING.match(line)
        if m:
            out["headings"].append((len(m.group(1)), m.group(2)))
        if line.lstrip().startswith("|"):
            run += 1
        elif run:
            out["tables"].append(run)
            run = 0
        out["images"] += IMG.findall(line)
        out["anchors"] += ANCHOR.findall(line)
        out["urls"] += URL.findall(line)
    if run:
        out["tables"].append(run)
    return out


def toc_expected(text, eol="\n"):
    """見出しから目次ブロックの中身（行のリスト）を作る。"""
    cmd = TOC_CMD.search(text)
    opts = dict(re.findall(r"(\w+)=(\w+)", cmd.group(1))) if cmd else {}
    lo, hi = int(opts.get("depthFrom", 1)), int(opts.get("depthTo", 6))
    seen, items = {}, []
    heads = parse(text)["headings"]
    # この手順書の慣習: 最初の「# 見出し」より前にある見出し（変更履歴など）は目次に載せない
    first_h1 = next((i for i, h in enumerate(heads) if h[0] == 1), 0)
    for i, (level, title) in enumerate(heads):
        a = slug(title, seen)
        if i >= first_h1 and lo <= level <= hi:
            link = title.replace("&", "\\&") if "\\&" not in title else title
            items.append(f"{'  ' * (level - lo)}- [{link}](#{a})")
    return items


def toc_block(text):
    b, e = text.find(TOC_BEGIN), text.find(TOC_END)
    if b < 0 or e < 0 or e < b:
        return None
    return b + len(TOC_BEGIN), e


def toc_actual(text):
    span = toc_block(text)
    if span is None:
        return None
    return [l for l in text[span[0]:span[1]].splitlines() if l.strip()]


def cmd_toc_check(path):
    text = Path(path).read_text(encoding="utf-8")
    actual = toc_actual(text)
    if actual is None:
        print("[NG] 目次ブロック（<!-- code_chunk_output -->）が見つからない")
        return 1
    expected = toc_expected(text)
    if actual == expected:
        print(f"[OK] 目次は見出しと一致（{len(actual)} 項目）")
        return 0
    print(f"[NG] 目次が見出しと一致しない（現在 {len(actual)} / 期待 {len(expected)} 項目）")
    for a, b in zip(actual + [""] * len(expected), expected + [""] * len(actual)):
        if a != b:
            print(f"   現在: {a}\n   期待: {b}")
            break
    return 1


def cmd_toc_write(path):
    p = Path(path)
    raw = p.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    span = toc_block(text)
    if span is None:
        print("[NG] 目次ブロックが見つからない")
        return 1
    body = "\n\n" + "\n".join(toc_expected(text)) + "\n\n"
    new = text[:span[0]] + body + text[span[1]:]
    p.write_bytes(new.replace("\n", eol).encode("utf-8"))
    print(f"[OK] 目次を更新した（{len(toc_expected(text))} 項目、改行={'CRLF' if eol == chr(13) + chr(10) else 'LF'}）")
    return 0


def cmd_eol_match(ja_path, en_path):
    ja = Path(ja_path).read_bytes()
    want = "\r\n" if ja.count(b"\r\n") > ja.count(b"\n") / 2 else "\n"
    p = Path(en_path)
    text = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
    p.write_bytes(text.replace("\n", want).encode("utf-8"))
    print(f"[OK] 改行コードを {'CRLF' if want == chr(13) + chr(10) else 'LF'} に揃えた: {en_path}")
    return 0


def eol_kind(raw):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    return crlf, lf


def cmd_compare(ja_path, en_path):
    ja_p, en_p = Path(ja_path), Path(en_path)
    ja_raw, en_raw = ja_p.read_bytes(), en_p.read_bytes()
    ja, en = ja_raw.decode("utf-8"), en_raw.decode("utf-8")
    failed = False

    def ng(msg):
        nonlocal failed
        failed = True
        print(f"[NG] {msg}")

    # 改行コード
    jc, jl = eol_kind(ja_raw)
    ec, el = eol_kind(en_raw)
    ja_kind = "CRLF" if jc and not jl else "LF" if jl and not jc else "混在"
    en_kind = "CRLF" if ec and not el else "LF" if el and not ec else "混在"
    if ja_kind == en_kind and en_kind != "混在":
        print(f"[OK] 改行コード: {en_kind}（原文と一致）")
    else:
        ng(f"改行コード: 原文 {ja_kind} / 英語版 {en_kind}")

    pj, pe = parse(ja), parse(en)

    # 見出し
    hj, he = pj["headings"], pe["headings"]
    lv_j, lv_e = [h[0] for h in hj], [h[0] for h in he]
    num_j = [(NUMBER.match(h[1]) or [None, None])[1] for h in hj]
    num_e = [(NUMBER.match(h[1]) or [None, None])[1] for h in he]
    if lv_j == lv_e and num_j == num_e:
        print(f"[OK] 見出し: {len(he)} 個、階層と番号が原文と一致")
    else:
        ng(f"見出しの数・階層・番号が不一致（原文 {len(hj)} / 英語版 {len(he)}）")
        for i, (a, b) in enumerate(zip(zip(lv_j, num_j), zip(lv_e, num_e))):
            if a != b:
                print(f"   {i + 1} 番目: 原文 {hj[i]} / 英語版 {he[i]}")
                break

    # 改ページ
    if pj["breaks"] == pe["breaks"]:
        print(f"[OK] 改ページ: {len(pe['breaks'])} か所、位置が原文と一致")
    else:
        ng(f"改ページの数・位置が不一致（原文 {len(pj['breaks'])} / 英語版 {len(pe['breaks'])}）")

    # 表
    if pj["tables"] == pe["tables"]:
        print(f"[OK] 表: {len(pe['tables'])} 個、行数が一致")
    else:
        ng(f"表の数・行数が不一致（原文 {pj['tables']} / 英語版 {pe['tables']}）")

    # コードブロック: 日本語を含まない行は同一であること
    if len(pj["fences"]) != len(pe["fences"]):
        ng(f"コードブロック数が不一致（原文 {len(pj['fences'])} / 英語版 {len(pe['fences'])}）")
    else:
        bad = 0
        for i, (a, b) in enumerate(zip(pj["fences"], pe["fences"]), 1):
            keep = [l for l in a if l.strip() and not CJK.search(l)]
            it = iter([l for l in b])
            if not all(any(k == x for x in it) for k in keep):
                ng(f"コードブロック {i} のコマンド行が原文と異なる")
                bad += 1
        if not bad:
            print(f"[OK] コードブロック: {len(pe['fences'])} 個、コマンド行は原文と同一")

    # 画像
    if len(pj["images"]) != len(pe["images"]):
        ng(f"画像参照の数が不一致（原文 {len(pj['images'])} / 英語版 {len(pe['images'])}）")
    missing = [r for r in pe["images"] if not r.startswith(("http://", "https://", "data:"))
               and not (en_p.parent / r.split("?")[0]).is_file()]
    if missing:
        ng(f"画像参照が実在しない: {missing}")
    elif len(pj["images"]) == len(pe["images"]):
        print(f"[OK] 画像参照: {len(pe['images'])} 件、すべて実在する")
    diff_img = [(a, b) for a, b in zip(pj["images"], pe["images"]) if a != b]
    for a, b in diff_img:
        print(f"[INFO] 画像を差し替え: {a} → {b}")

    # 内部リンク
    seen, anchors = {}, set()
    for _, title in he:
        anchors.add(slug(title, seen))
    dead = sorted({a for a in pe["anchors"] if a not in anchors})
    if dead:
        ng(f"解決できない内部リンク: {dead[:5]}{' …' if len(dead) > 5 else ''}")
    else:
        print(f"[OK] 内部リンク: {len(pe['anchors'])} 件、すべて見出しに解決する")

    # 目次
    actual = toc_actual(en)
    if actual is None:
        ng("目次ブロックが見つからない")
    elif actual == toc_expected(en):
        print(f"[OK] 目次は見出しと一致（{len(actual)} 項目）")
    else:
        ng("目次が見出しと一致しない（toc-write で作り直す）")

    # 可視テキストの日本語・全角記号
    vis = "\n".join(pe["visible"])
    cjk = sorted(set(CJK.findall(vis)))
    full = sorted({c for c in FULLWIDTH.findall(vis) if c not in KEEP_FULLWIDTH})
    if cjk:
        ng(f"可視テキストに日本語が残っている: {''.join(cjk)}")
    if full:
        ng(f"可視テキストに全角記号が残っている: {''.join(full)}")
    if not cjk and not full:
        print("[OK] 可視テキストに日本語・全角記号の残りなし")

    # コメント・コードブロック内の日本語
    hidden = [c for c in COMMENT.findall(en) if CJK.search(c)]
    in_code = [l for f in pe["fences"] for l in f if CJK.search(l)]
    if hidden:
        print(f"[WARN] HTML コメント内に日本語が残っている（{len(hidden)} か所。改訂履歴など）")
    if in_code:
        print(f"[WARN] コードブロック内に日本語が残っている（{len(in_code)} 行）: {in_code[0].strip()[:50]}")

    # URL
    uj, ue = set(pj["urls"]), set(pe["urls"])
    for u in sorted(uj - ue):
        print(f"[INFO] 原文にあり英語版にない URL: {u}")
    for u in sorted(ue - uj):
        print(f"[INFO] 英語版で追加・変更された URL: {u}")

    return 1 if failed else 0


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "toc-check":
        sys.exit(cmd_toc_check(a[1]))
    if len(a) == 2 and a[0] == "toc-write":
        sys.exit(cmd_toc_write(a[1]))
    if len(a) == 3 and a[0] == "eol-match":
        sys.exit(cmd_eol_match(a[1], a[2]))
    if len(a) == 3 and a[0] == "compare":
        sys.exit(cmd_compare(a[1], a[2]))
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
