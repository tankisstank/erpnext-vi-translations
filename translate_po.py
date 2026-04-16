#!/usr/bin/env python3
"""Translate empty msgstr entries in .po files using gemma-4 (local vLLM).
Usage: python3 translate_po.py <input.po> [--limit N] [--batch 80]
Writes in-place. Preserves headers, comments, placeholders.
"""
import re, json, sys, time, urllib.request, urllib.error, argparse

LLM_URL = 'http://lkf1:8002/v1/chat/completions'
MODEL = '/home/lkf1/models/gemma-4-26B-A4B-it-AWQ-4bit'

SYSTEM = ("Bạn là dịch giả ERP tiếng Việt chuyên nghiệp. Dịch các cụm tiếng Anh sang tiếng Việt theo NGỮ CẢNH doanh nghiệp/quản trị (ERPNext). "
          "QUY TẮC:\n"
          "- GIỮ NGUYÊN placeholder: {0}, {name}, %(x)s, %d, %s, <a>, </b>, v.v.\n"
          "- Ngắn gọn, chuẩn thuật ngữ kinh doanh VN\n"
          "- Ví dụ: Submit=Xác nhận, Save=Lưu, Customer=Khách hàng, Supplier=Nhà cung cấp, "
          "Invoice=Hóa đơn, Payment=Thanh toán, Draft=Nháp, Amount=Số tiền, Quantity=Số lượng, Rate=Đơn giá, Total=Tổng\n"
          "- Trả lời CHÍNH XÁC JSON array dạng [\"dịch 1\", \"dịch 2\", ...] "
          "không kèm markdown, không giải thích. Số lượng phần tử = số lượng input.")


def unescape(s):
    return s.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')


def escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')


def parse_po(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Split into blocks by blank line
    blocks = re.split(r'\n\n+', text)
    entries = []
    header = blocks[0]
    for block in blocks[1:]:
        lines = block.split('\n')
        msgid_lines = []
        msgstr_lines = []
        section = None
        meta = []  # preserve comments and msgctxt
        for line in lines:
            if line.startswith('msgid '):
                section = 'id'
                msgid_lines.append(line[6:].strip()[1:-1])
            elif line.startswith('msgstr '):
                section = 'str'
                msgstr_lines.append(line[7:].strip()[1:-1])
            elif line.startswith('"') and section == 'id':
                msgid_lines.append(line.strip()[1:-1])
            elif line.startswith('"') and section == 'str':
                msgstr_lines.append(line.strip()[1:-1])
            else:
                meta.append(line)
        if msgid_lines:
            entries.append({
                'meta': meta,
                'msgid_parts': msgid_lines,
                'msgstr_parts': msgstr_lines,
                'msgid': unescape(''.join(msgid_lines)),
                'msgstr': unescape(''.join(msgstr_lines)),
            })
    return header, entries


def write_po(path, header, entries):
    out = [header]
    for e in entries:
        block = list(e['meta'])
        msgid = e['msgid']
        msgstr = e['msgstr']
        msgid_esc = escape(msgid)
        msgstr_esc = escape(msgstr)
        block.append(f'msgid "{msgid_esc}"')
        block.append(f'msgstr "{msgstr_esc}"')
        out.append('\n'.join(b for b in block if b is not None))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(out) + '\n')


def call_llm(msgids):
    prompt = '\n'.join(f'{i+1}. {m}' for i, m in enumerate(msgids))
    body = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': f'Dịch sang tiếng Việt (trả JSON array):\n{prompt}'},
        ],
        'temperature': 0.1,
        'max_tokens': 4096,
    }
    req = urllib.request.Request(
        LLM_URL,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        r = json.loads(resp.read())
    text = r['choices'][0]['message']['content']
    # Clean markdown fence
    text = re.sub(r'^```(?:json)?', '', text.strip())
    text = re.sub(r'```$', '', text.strip())
    try:
        arr = json.loads(text)
        if isinstance(arr, list):
            return arr
    except Exception:
        pass
    raise RuntimeError(f'LLM non-JSON: {text[:200]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--batch', type=int, default=80)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    header, entries = parse_po(args.path)
    empty = [i for i, e in enumerate(entries)
             if e['msgid'] and not e['msgstr'] and len(e['msgid']) < 500]
    total = len(empty)
    if args.limit:
        empty = empty[:args.limit]
    print(f'File {args.path}: {total} untranslated, processing {len(empty)}', flush=True)

    for start in range(0, len(empty), args.batch):
        batch = empty[start:start+args.batch]
        msgids = [entries[i]['msgid'] for i in batch]
        try:
            translations = call_llm(msgids)
        except Exception as e:
            print(f'  batch {start} failed: {e}', flush=True)
            continue
        if len(translations) != len(batch):
            print(f'  batch {start}: size mismatch ({len(translations)} vs {len(batch)}), skipping', flush=True)
            continue
        for idx, trans in zip(batch, translations):
            entries[idx]['msgstr'] = trans
        done = start + len(batch)
        print(f'  translated {done}/{len(empty)}', flush=True)

    if not args.dry_run:
        write_po(args.path, header, entries)
        print('Saved.', flush=True)

if __name__ == '__main__':
    main()
