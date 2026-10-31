from pathlib import Path
import runpy

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'rr-calendar-v1' in s:
    runpy.run_path('.github/scripts/patch_v321.py', run_name='__main__')
    raise SystemExit(0)
raise SystemExit('Expected Race Ready calendar before v3.2.1 patch')

# deployment trigger: corrected v3.2.1 multi-week calendar patch
