"""Rebuild dashboard payload from FY12-FY26 combined data."""
import pickle, json, re
from pathlib import Path
from collections import defaultdict

ALL_LINES = pickle.loads(Path(r'C:\Dev\CheckRegister\Working Folder\Cache and Tools\build\combined_lines.pkl').read_bytes())
print(f'Loaded: {len(ALL_LINES):,} rows', flush=True)

INSTRUCTIONAL = {
    'Instruction — Substitute Teachers (General Classes)',
    'Support — Instructional Staff (PD/Curriculum)',
    'Instruction — Basic Programs (Elementary/Secondary)',
    'Instruction — Substitute Teachers (Special Education)',
    'Instruction — Compensatory Education',
    'Instruction — Special Education',
    'Instruction — Vocational / CTE',
}

def slug(s):
    s = s.lower().replace('—','-').replace('/','-').replace('(','').replace(')','')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def build_section(lines, fy_list):
    totals = {fy: 0.0 for fy in fy_list}
    line_count = 0
    cats = defaultdict(lambda: {
        'byYear': defaultdict(float),
        'countByYear': defaultdict(int),
        'vendorsByYear': defaultdict(lambda: defaultdict(lambda: {'t': 0.0, 'n': 0, 'descs': defaultdict(lambda: [0.0, 0])})),
    })
    for r in lines:
        fy = r['Fiscal Year']
        if fy not in totals: continue
        cat = r.get('Category','') or 'Untyped (function code blank or 000)'
        amt = r['Amount']
        totals[fy] += amt
        line_count += 1
        cats[cat]['byYear'][fy] += amt
        cats[cat]['countByYear'][fy] += 1
        v = r['Vendor Name'] or '?'
        d = (r['Description'] or '').strip()
        vrec = cats[cat]['vendorsByYear'][fy][v]
        vrec['t'] += amt
        vrec['n'] += 1
        vrec['descs'][d][0] += amt
        vrec['descs'][d][1] += 1
    grand = sum(totals.values())
    out_cats = {}
    for cat, info in cats.items():
        vbyy = {}
        for fy, vendors in info['vendorsByYear'].items():
            sorted_vs = sorted(vendors.items(), key=lambda x: -x[1]['t'])[:25]
            vbyy[fy] = []
            for vname, vdata in sorted_vs:
                top_descs = sorted(vdata['descs'].items(), key=lambda x: -x[1][0])[:20]
                vbyy[fy].append({
                    'v': vname, 't': round(vdata['t'], 2), 'n': vdata['n'],
                    'i': [{'d': d, 'a': round(a, 2), 'c': c} for d, (a, c) in top_descs]
                })
        out_cats[cat] = {
            'slug': slug(cat),
            'total': round(sum(info['byYear'].values()), 2),
            'instructional': cat in INSTRUCTIONAL,
            'byYear': {fy: round(v, 2) for fy, v in info['byYear'].items()},
            'countByYear': dict(info['countByYear']),
            'vendorsByYear': vbyy,
        }
    return {
        'totals': {fy: round(v, 2) for fy, v in totals.items()},
        'grandTotal': round(grand, 2),
        'lineCount': line_count,
        'categories': out_cats,
    }

def build_subjects(lines, fy_list):
    pd_lines = [r for r in lines if r['Budget Unit'].startswith('101425221')]
    sub_agg = defaultdict(lambda: {fy: 0.0 for fy in fy_list})
    sub_count = defaultdict(int)
    for r in pd_lines:
        s = r.get('Subject') or 'Not Directly Attributable'
        sub_agg[s][r['Fiscal Year']] += r['Amount']
        sub_count[s] += 1
    out = {}
    for s, byfy in sub_agg.items():
        out[s] = {
            'lines': sub_count[s],
            'byYear': {fy: round(v, 2) for fy, v in byfy.items()},
            'total': round(sum(byfy.values()), 2),
        }
    return out

fys = sorted({r['Fiscal Year'] for r in ALL_LINES})
operating = [r for r in ALL_LINES if not (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
bond = [r for r in ALL_LINES if (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
print(f'FYs: {fys}', flush=True)
print(f'Operating: {len(operating):,} | Bond: {len(bond):,}', flush=True)

payload = {
    'fy': fys,
    'all': build_section(ALL_LINES, fys),
    'operating': build_section(operating, fys),
    'bond': build_section(bond, fys),
    'meta': {'totalLines': len(ALL_LINES), 'fyRange': f'{fys[0]}-{fys[-1]}', 'sourceCount': 152},
}
payload['all']['subjects'] = build_subjects(ALL_LINES, fys)

print(f'Grand total: ${payload["all"]["grandTotal"]:,.2f}', flush=True)

new_payload = json.dumps(payload, separators=(',', ':'))
out = Path(r'C:\Dev\CheckRegister\Working Folder\Cache and Tools\build\payload.json')
out.write_text(new_payload, encoding='utf-8')
print(f'Saved {out} ({out.stat().st_size:,} bytes)', flush=True)

html_path = Path(r'C:\Dev\CheckRegister\index.html')
html = html_path.read_text(encoding='utf-8')
html = re.sub(
    r'(<script id="data-payload"[^>]*>).*?(</script>)',
    lambda m: m.group(1) + new_payload + m.group(2),
    html, count=1, flags=re.DOTALL
)
fy_range = f'FY{fys[0][2:]}-{fys[-1]}'
html = re.sub(r'FY\d\d-FY\d\d', fy_range, html)
def fmt_m(n): return f'${n/1_000_000:.0f}M'
total = payload['all']['grandTotal']
op_total = payload['operating']['grandTotal']
bond_total = payload['bond']['grandTotal']
html = re.sub(
    r'\d+,?\d* line items, \$\d+M total — split into operating \(\$\d+M\) and bond/capital \(\$\d+M\) views\.',
    f'{payload["all"]["lineCount"]:,} line items, {fmt_m(total)} total — split into operating ({fmt_m(op_total)}) and bond/capital ({fmt_m(bond_total)}) views.',
    html
)
html = re.sub(r'\d+ monthly check register PDFs', f'{payload["meta"]["sourceCount"]} monthly check register PDFs', html)
html_path.write_text(html, encoding='utf-8')
print(f'Updated {html_path} ({html_path.stat().st_size:,} bytes)', flush=True)
