"""Rebuild combined dataset after bundle-date fix.
- Load new pre2020_lines.pkl (with corrected meeting dates)
- Append Oct 2019 recovered rows (still needed because pypdf fallback was added mid-run)
- Append FY21+ all_lines.pkl
- Add Issue Date FY column
- Apply categorization + subject classification
- Save combined_lines.pkl, then defer to build_combined_wb.py for workbook"""
import sys, pickle
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from categorize_v2 import categorize, VENDOR_CATS

BUILD = Path(__file__).parent
pre = pickle.loads((BUILD / 'pre2020_lines.pkl').read_bytes())
oct19 = pickle.loads((BUILD / 'oct2019_recovered.pkl').read_bytes())
post = pickle.loads((BUILD / 'all_lines.pkl').read_bytes())
print(f'Pre-2020 (re-extracted): {len(pre):,}', flush=True)
print(f'Oct 2019 recovered:      {len(oct19):,}', flush=True)
print(f'FY21-FY26 standalone:    {len(post):,}', flush=True)

# Pre-2020 doesn't have Category/Subject/Confidence yet
for r in pre:
    r.setdefault('Category', '')
    r.setdefault('Subject', '')
    r.setdefault('Confidence', '')

combined = pre + oct19 + post
print(f'Combined: {len(combined):,}', flush=True)

# Add Issue Date FY
def issue_fy(d):
    if not isinstance(d, datetime): return ''
    return f'FY{(d.year+1)%100:02d}' if d.month >= 7 else f'FY{d.year%100:02d}'

VENDOR_SUBJECT = pickle.loads(Path(r'C:\Users\Alex\AppData\Local\Temp\vendor_subject.pkl').read_bytes())

def classify_subject(vendor, desc):
    if not vendor: return 'Not Directly Attributable'
    for v_key, subj in VENDOR_SUBJECT.items():
        if vendor.startswith(v_key[:15]):
            return subj
    d = (desc or '').upper()
    if any(k in d for k in ('READING','WRITING','LITERACY','CALKINS','F&P','FOUNTAS')): return 'ELA'
    if any(k in d for k in ('MATH','AVMR','MRSP','BRIDGES','ALGEBRA','GEOMETRY')): return 'Math'
    if 'SCIENCE' in d: return 'Science'
    if 'SOCIAL' in d: return 'Social Studies'
    return 'Not Directly Attributable'

print('Re-applying categorization + subjects + Issue-Date FY...', flush=True)
for r in combined:
    r['Issue Date FY'] = issue_fy(r['Issue Date'])
    r['Category'] = categorize(r.get('Vendor Name',''), r.get('Fund',''),
                              r.get('Function Code',''), r.get('Account',''),
                              r.get('Budget Unit',''), r.get('Amount', 0))
    if r.get('Budget Unit','').startswith('101425221'):
        r['Subject'] = classify_subject(r.get('Vendor Name',''), r.get('Description',''))
        v = r.get('Vendor Name','')
        if v and any(v.startswith(vk[:15]) for vk in VENDOR_SUBJECT):
            r['Confidence'] = 'high'
        elif r.get('Subject') != 'Not Directly Attributable':
            r['Confidence'] = 'med'
        else:
            r['Confidence'] = 'low'
    else:
        r['Subject'] = ''
        r['Confidence'] = ''

(BUILD / 'combined_lines.pkl').write_bytes(pickle.dumps(combined))
print(f'Saved combined_lines.pkl: {len(combined):,} rows', flush=True)

# FY breakdown
mfys = Counter(r['Fiscal Year'] for r in combined)
ifys = Counter(r['Issue Date FY'] for r in combined if r['Issue Date FY'])
print(f'\nMeeting-FY breakdown:')
for fy in sorted(mfys): print(f'  {fy}: {mfys[fy]:,}')
print(f'\nIssue-Date FY breakdown:')
for fy in sorted(ifys): print(f'  {fy}: {ifys[fy]:,}')
print(f'\nGrand total: ${sum(r["Amount"] for r in combined):,.2f}')
