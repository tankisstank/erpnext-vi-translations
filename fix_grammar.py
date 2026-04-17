#!/usr/bin/env python3
"""
Fix Vietnamese grammar in Frappe .po files.

Rules applied to every msgstr:
  1. Swap placeholder order: "{N} <vi-phrase>" → "<vi-phrase> {N}"
     for a fixed set of Vietnamese noun-phrase suffixes.
     Reason: English uses <Noun><Qualifier>; Vietnamese uses
     <Qualifier><Noun>. LLM translations often preserved EN order.
  2. Lowercase noun part (Vietnamese convention: only first word
     of sentence is capitalized, not every word).

Usage: python3 fix_grammar.py <file.po> [<file2.po>...]
"""
import re
import sys

# VN qualifier phrases that should come BEFORE the noun/placeholder.
# Ordered longest-first so longer matches take precedence.
VN_QUALIFIERS = [
    "Bảng điều khiển",
    "Trang tổng quan",
    "Cài đặt chế độ xem danh sách",
    "Cài đặt",
    "Báo cáo",
    "Danh sách",
    "Danh mục",
    "Lịch sử",
    "Tóm tắt",
    "Chi tiết",
    "Bảng điều hành",
    "Bảng",
    "Biểu mẫu",
    "Mẫu",
    "Nhóm",
    "Loại",
    "Quyền",
    "Xem",
    "Cây",
    "Mã",
    "Số",
    "Ngày",
    "Số tiền",
    "Tổng",
    "Trạng thái",
    "Chủ sở hữu",
    "Địa chỉ",
    "Giá",
    "Giá trị",
    "Bản ghi",
    "Đơn",
    "Hóa đơn",
    "Phiếu nhận",
    "Ghi chú",
    "Mô tả",
]


def fix_msgstr(msgstr: str) -> str:
    """Apply grammar-flip rules to a single msgstr line."""
    for phrase in VN_QUALIFIERS:
        # Pattern: "{N} <phrase>" → "<phrase> {N}"
        # Allow the phrase to be at end-of-string, before space, or before quote.
        pat = r"\{(\d+)\}\s+" + re.escape(phrase) + r"(?=\s|$|\"|,|\.|:)"
        msgstr = re.sub(pat, lambda m: f"{phrase} {{{m.group(1)}}}", msgstr)
        # Also lowercase-variant: "{N} <phrase-lowered>"
        lower_phrase = phrase[0].lower() + phrase[1:]
        if lower_phrase != phrase:
            pat = r"\{(\d+)\}\s+" + re.escape(lower_phrase) + r"(?=\s|$|\"|,|\.|:)"
            msgstr = re.sub(pat, lambda m: f"{phrase} {{{m.group(1)}}}", msgstr)
    return msgstr


def process(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = re.split(r"\n\n+", text)
    changed = 0
    new_blocks = [blocks[0]]  # keep header

    for b in blocks[1:]:
        m = re.search(r'^msgstr "(.*)"$', b, re.MULTILINE)
        if not m:
            new_blocks.append(b)
            continue
        msgstr = m.group(1)
        if "\n" in msgstr:
            new_blocks.append(b)
            continue
        new_msgstr = fix_msgstr(msgstr)
        if new_msgstr != msgstr:
            changed += 1
            b = re.sub(
                r'^msgstr "(.*)"$',
                'msgstr "' + new_msgstr.replace("\\", "\\\\").replace('"', '\\"') + '"',
                b,
                count=1,
                flags=re.MULTILINE,
            )
        new_blocks.append(b)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(new_blocks))

    return changed


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_grammar.py <file.po> [<file2.po>...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        changed = process(p)
        print(f"{p}: flipped {changed} msgstrs")


if __name__ == "__main__":
    main()
