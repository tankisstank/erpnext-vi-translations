# ERPNext Vietnamese Translations (Bản dịch tiếng Việt)

Complete Vietnamese translations for **Frappe Framework v16**, **ERPNext v16**, and **Frappe HRMS v16**.
Ready to drop into your ERPNext deployment.

Bản dịch tiếng Việt đầy đủ cho Frappe, ERPNext, và HRMS phiên bản 16. Copy vào là dùng được ngay.

## Why this exists

The official `vi.po` files in Frappe's `version-16` branch are **nearly empty** (only ~5-8 strings translated per app). This repo provides a near-complete Vietnamese translation so Vietnamese businesses can use ERPNext in their native language today, without waiting for community Crowdin progress.

`vi.po` chính thức trong Frappe `version-16` gần như trống. Repo này cung cấp bản dịch gần đầy đủ để doanh nghiệp Việt dùng ngay.

## Coverage / Thống kê

| App | msgid | Translated | Coverage |
|---|---|---|---|
| frappe | ~6,100 | ~6,100 | ≈100% |
| erpnext | ~9,300 | ~9,300 | ≈100% |
| hrms | ~2,200 | ~2,200 | ≈100% |

**Total: ~17,600 translated strings.**

## Origin / Cách thực hiện

1. Base translations taken from the `develop` branch on GitHub (more complete than `version-16`)
2. Remaining ~11,000 empty `msgstr` entries were translated using **gemma-4-26B** (multilingual LLM) with business/ERP-oriented prompts
3. Key business terms hard-coded in prompt for consistency:
   - Submit = Xác nhận
   - Save = Lưu
   - Customer = Khách hàng
   - Supplier = Nhà cung cấp
   - Invoice = Hóa đơn
   - Payment = Thanh toán
   - Draft = Nháp
   - Amount = Số tiền
   - Quantity = Số lượng
   - Rate = Đơn giá
   - Total = Tổng
4. Placeholders (`{0}`, `{name}`, `%(x)s`, HTML tags) preserved where present

## Curated accounting terminology and template repairs — 2026-09-06

Commit [`fc82cda`](https://github.com/tankisstank/erpnext-vi-translations/commit/fc82cdaf9d81cb1812d32a4fabeb3ca173e361c1)
adds a focused editorial pass to the Frappe and ERPNext catalogs. Accounting
terminology was cross-checked against
[`mrhuychien/erpnextvn`](https://github.com/mrhuychien/erpnextvn), then chosen
for clarity in standard ERPNext workflows rather than copied wholesale.

- `Submit` / `Submitted` → `Xác nhận` / `Đã xác nhận`
- `Posting Date` → `Ngày hạch toán`; `Trial Balance` → `Bảng cân đối phát sinh`
- `VAT` → `Thuế GTGT`; `Net Total` → `Tổng trước thuế`
- `Expense Claim` → `Đề nghị thanh toán`; `Purchase Receipt` → `Phiếu nhập kho`
- `Payment Entry` → `Chứng từ thanh toán`, to cover both receipts/payments and
  ERPNext transfers; `Stock Entry` remains `Phiếu xuất nhập kho`.

Nine malformed translations were also repaired. These include a Notification
HTML/Jinja example and ERPNext messages with positional placeholders. The
repairs preserve Jinja directives and required placeholders rather than
translating template syntax.

Validation on the resulting catalogs covered 17,631 entries across Frappe,
ERPNext, and HRMS, with **0 placeholder/Jinja mismatches**. `VAT` is included
as an explicit ERPNext glossary entry because the base catalog did not contain
it as a standalone `msgid`.

Tóm tắt tiếng Việt: bản hiệu đính chuẩn hóa thuật ngữ kế toán, sửa chín chuỗi
lỗi placeholder/Jinja và đã kiểm tra toàn bộ 17.631 entry không còn mismatch.
Các thay đổi chỉ thuộc locale giao diện, không phải bộ quy tắc tuân thủ kế toán
hoặc thuế Việt Nam.

## Quality note

Most strings are LLM-translated. They are **usable but not hand-curated**. Community contributions via Crowdin (the official channel for Frappe translations) are still the gold standard. This repo is a **practical bootstrap** until Crowdin coverage catches up.

Bản dịch chủ yếu bằng LLM. Dùng được nhưng chưa được review thủ công. Nếu anh muốn bản chính thức xác định, hãy tham gia Crowdin.

## Usage / Cách dùng

### Docker-based ERPNext (khuyến nghị)

```bash
# 1. Clone this repo
git clone https://github.com/<user>/erpnext-vi-translations
cd erpnext-vi-translations

# 2. Copy the .po files into your ERPNext container
docker cp frappe/locale/vi.po  erpnext-backend:/home/frappe/frappe-bench/apps/frappe/frappe/locale/vi.po
docker cp erpnext/locale/vi.po erpnext-backend:/home/frappe/frappe-bench/apps/erpnext/erpnext/locale/vi.po
# Run this only when HRMS is installed:
docker cp hrms/locale/vi.po    erpnext-backend:/home/frappe/frappe-bench/apps/hrms/hrms/locale/vi.po

# 3. Compile .po → .mo
docker exec erpnext-backend bench --site <your-site> compile-po-to-mo

# 4. Clear cache + restart
docker exec erpnext-backend bench --site <your-site> clear-cache
docker restart erpnext-backend
```

### Native bench

```bash
# Inside frappe-bench directory
cp /path/to/frappe.vi.po  apps/frappe/frappe/locale/vi.po
cp /path/to/erpnext.vi.po apps/erpnext/erpnext/locale/vi.po
cp /path/to/hrms.vi.po    apps/hrms/hrms/locale/vi.po

bench --site <your-site> compile-po-to-mo
bench --site <your-site> clear-cache
bench restart
```

### Switch user to Vietnamese

Go to **User → Settings → Language → Vietnamese**, or globally via **Setup → System Settings → Language → vi**.

## Vietnamese-specific settings

For Vietnamese businesses, also configure:

```
System Settings:
  - Language: vi
  - Number Format: #.###,##   (1.234.567,89)
  - Date Format: dd-mm-yyyy   (16-04-2026)
  - Time Zone: Asia/Ho_Chi_Minh
  - First Day of Week: Monday

VND Currency:
  - Symbol: đ
  - Symbol on right: yes
  - Fraction: (empty — VND doesn't use cents)
  - smallest_currency_fraction_value: 0
```

## Updating / Bổ sung

When Frappe releases a newer `vi.po`:

```bash
# Diff to find new strings
diff <(curl -sL https://raw.githubusercontent.com/frappe/frappe/develop/frappe/locale/vi.po) frappe/locale/vi.po

# Use translate_po.py to translate new msgids via gemma-4 (requires local vLLM)
python3 translate_po.py frappe/locale/vi.po --batch 80
```

See `translate_po.py` for the auto-translation script.

## Contributing

- **Officially**: contribute at https://crowdin.com/project/frappe (Vietnamese team)
- **Here**: PRs welcome for corrections. Please note which `msgid` you're improving and why.

## License

These translations follow the same license as the upstream Frappe projects: **MIT** for Frappe Framework, **GPL v3** for ERPNext and HRMS.

## Credits

- Upstream English source: Frappe Technologies Pvt. Ltd. and contributors
- Base Vietnamese translations: Crowdin community contributors
- Auto-translation for gaps: gemma-4-26B (via vLLM)
- Curation and deployment: LKF Cold Chain — Vietnam
