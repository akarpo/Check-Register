"""Categorization v2 — vendor lookup with fund/function disambiguation for multi-cat vendors."""
from __future__ import annotations
import json, pickle
from pathlib import Path
from collections import defaultdict

PAYLOAD = json.loads(Path(r'C:\Users\Alex\AppData\Local\Temp\dashboard_payload.json').read_text(encoding='utf-8'))
VENDOR_CATS = defaultdict(lambda: defaultdict(float))
for cat, data in PAYLOAD['all']['categories'].items():
    for fy, vlist in data.get('vendorsByYear', {}).items():
        for v in vlist:
            VENDOR_CATS[v['v']][cat] += v['t']
VENDOR_CATS = {v: dict(c) for v, c in VENDOR_CATS.items()}


def categorize(vendor, fund, func, account, bu, amt):
    fund = (fund or '').strip()
    func = (func or '').strip()
    account = (account or '').strip()
    bu = (bu or '').strip()
    cats = VENDOR_CATS.get(vendor or '')
    if not cats:
        return _default_categorize(fund, func, account, bu, amt)
    if len(cats) == 1:
        return list(cats.keys())[0]

    # Multi-category vendor — disambiguate via signature
    f2 = func[:2] if len(func) >= 2 else func
    f3 = func[:3] if len(func) >= 3 else func

    def maybe(name):
        return name if name in cats else None

    # Substitute teacher payroll (account L4026) — categorize by fund
    if account == 'L4026':
        if fund == '101':
            return maybe('Instruction — Substitute Teachers (General Classes)') or _max(cats)
        if fund == '122':
            return maybe('Instruction — Substitute Teachers (Special Education)') or _max(cats)
        if fund == '531':
            return maybe('Community — Childcare / Latchkey') or _max(cats)
        if fund == '530':
            return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
        if fund == '120':
            return maybe('Instruction — Compensatory Education') or _max(cats)

    # Function-code first
    if f3 in ('111','112','113','114','115','116','117','118','119'):
        return maybe('Instruction — Basic Programs (Elementary/Secondary)') or _max(cats)
    if f3 == '122':
        return maybe('Instruction — Special Education') or _max(cats)
    if f3 == '125':
        return maybe('Instruction — Compensatory Education') or _max(cats)
    if f2 == '13':
        return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
    if f2 == '14':
        return maybe('Instruction — Vocational / CTE') or _max(cats)
    if f2 == '21':
        return maybe('Support — Pupil Services (Counsel/Health/Psych)') or _max(cats)
    if f2 == '22':
        return maybe('Support — Instructional Staff (PD/Curriculum)') or _max(cats)
    if f2 == '23':
        return maybe('Support — General Administration') or _max(cats)
    if f2 == '24':
        return maybe('Support — School Administration') or _max(cats)
    if f3 == '252':
        return maybe('Support — Business Services') or _max(cats)
    if f2 == '25':
        return maybe('Support — Central Services / Personnel') or _max(cats)
    if f2 == '26':
        return maybe('Support — Operations & Maintenance') or _max(cats)
    if f2 == '27':
        return maybe('Support — Transportation') or _max(cats)
    if f2 in ('28', '29'):
        return maybe('Support — Other') or _max(cats)
    if f2 == '33':
        return maybe('Community — Athletics & Activities') or _max(cats)
    if f2 in ('32', '34', '35', '39', '41'):
        return maybe('Community — Other Services') or _max(cats)
    if f2 in ('45', '46'):
        return maybe('Capital Outlay — Land/Buildings') or _max(cats)
    if f2 == '51':
        return maybe('Debt Service') or _max(cats)

    # No function code or unrecognized — use fund signal
    if not func or func == '000':
        if account.startswith('L'):
            return maybe('Payroll Deductions / Garnishments') or maybe('Untyped (function code blank or 000)') or _max(cats)
        if maybe('Untyped (function code blank or 000)'):
            return 'Untyped (function code blank or 000)'
    if fund == '520':
        return maybe('Food Service Fund — Untyped') or maybe('Food Service — Lunch Account Refunds') or _max(cats)
    if fund == '531':
        return maybe('Community — Childcare / Latchkey') or _max(cats)
    if fund == '529':
        return maybe('Instruction — Vocational / CTE') or _max(cats)
    if fund == '530':
        return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
    if fund in ('700', '701', '750'):
        return maybe('Student Activity Fund — Untyped') or _max(cats)
    if fund.startswith('4') and len(fund) == 3:
        return maybe('Capital Outlay — Land/Buildings') or _max(cats)
    if fund.startswith('3') and len(fund) == 3:
        return maybe('Debt Service') or _max(cats)
    return _max(cats)


def _max(cats):
    return max(cats.keys(), key=lambda k: cats[k])


def _default_categorize(fund, func, account, bu, amt):
    """For vendors not seen in FY23-FY26 payload — apply pure rule-based categorization."""
    f2 = func[:2] if len(func) >= 2 else func
    f3 = func[:3] if len(func) >= 3 else func
    sub_acct = account in ('1240', '1241')
    if f3 in ('111','112','113','114','115','116','117','118','119'):
        return 'Instruction — Substitute Teachers (General Classes)' if sub_acct else 'Instruction — Basic Programs (Elementary/Secondary)'
    if f3 == '122':
        return 'Instruction — Substitute Teachers (Special Education)' if sub_acct else 'Instruction — Special Education'
    if f3 == '125':
        return 'Instruction — Substitute Teachers (Special Education)' if sub_acct else 'Instruction — Compensatory Education'
    if f2 == '13': return 'Instruction — Adult / Continuing Ed'
    if f2 == '14': return 'Instruction — Vocational / CTE'
    if f2 == '21': return 'Support — Pupil Services (Counsel/Health/Psych)'
    if f2 == '22': return 'Support — Instructional Staff (PD/Curriculum)'
    if f2 == '23': return 'Support — General Administration'
    if f2 == '24': return 'Support — School Administration'
    if f3 == '252': return 'Support — Business Services'
    if f2 == '25': return 'Support — Central Services / Personnel'
    if f2 == '26': return 'Support — Operations & Maintenance'
    if f2 == '27': return 'Support — Transportation'
    if f2 in ('28', '29'): return 'Support — Other'
    if f2 == '33': return 'Community — Athletics & Activities'
    if f2 in ('32', '34', '35', '39', '41'): return 'Community — Other Services'
    if f2 in ('45', '46'): return 'Capital Outlay — Land/Buildings'
    if f2 == '51': return 'Debt Service'
    if account.startswith('L'): return 'Payroll Deductions / Garnishments'
    if fund.startswith('4') and len(fund) == 3: return 'Capital Outlay — Land/Buildings'
    if fund.startswith('3') and len(fund) == 3: return 'Debt Service'
    if fund == '520': return 'Food Service Fund — Untyped'
    if fund in ('700','701','750'): return 'Student Activity Fund — Untyped'
    if fund == '529': return 'Instruction — Vocational / CTE'
    if fund == '530': return 'Instruction — Adult / Continuing Ed'
    if fund == '531': return 'Community — Childcare / Latchkey'
    if bu and len(bu) <= 4: return 'Payroll Batch (Function not coded)'
    if amt < 0 and not func: return 'Refunds / Credits'
    return 'Untyped (function code blank or 000)'


if __name__ == '__main__':
    import openpyxl
    from collections import defaultdict
    wb = openpyxl.load_workbook(r'C:\Dev\CheckRegister\Troy_SD_Check_Register_FY23-FY26.xlsx', read_only=True, data_only=True)
    expected = {c: d['total'] for c, d in PAYLOAD['all']['categories'].items()}
    actual = defaultdict(float)
    for r in wb['All Lines'].iter_rows(values_only=True):
        if r[0] == 'Source Meeting': continue
        cat = categorize(r[9] or '', str(r[2] or ''), str(r[11] or ''),
                         str(r[12] or ''), str(r[10] or ''), r[15] or 0)
        actual[cat] += r[15] or 0
    print(f'{"Category":<55} {"Expected":>14} {"Actual":>14} {"Diff":>13} {"Pct":>6}')
    matched = 0
    total = sum(expected.values())
    for cat in sorted(expected, key=lambda c: -expected[c]):
        exp = expected[cat]; act = actual.get(cat, 0); diff = act - exp
        pct = (diff / exp * 100) if exp else 0
        threshold = max(5000, abs(exp) * 0.02)
        ok = 'OK' if abs(diff) < threshold else '  '
        print(f'{ok} {cat:<53} {exp:>14,.0f} {act:>14,.0f} {diff:>+13,.0f} {pct:>+5.1f}%')
        if abs(diff) < threshold: matched += abs(exp)
    print(f'\nGrand: ${sum(actual.values()):,.2f} (vs ${total:,.2f}, diff ${sum(actual.values())-total:+,.2f})')
    print(f'Match within $5K or 2%: {matched/total*100:.1f}%')
