"""Cache the course's pinned browser-Python runtime and packages for local use."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]/'.runtime/pyodide'
BASE='https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'
ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'ready.json').unlink(missing_ok=True)
def fetch(name):
    path=ROOT/name
    if not path.exists():
        with urllib.request.urlopen(BASE+name,timeout=120) as response:
            data=response.read()
        temp=path.with_suffix(path.suffix+'.part');temp.write_bytes(data);temp.replace(path)
    return name
fetch('pyodide-lock.json')
lock=json.loads((ROOT/'pyodide-lock.json').read_text())
packages=set()
def visit(name):
    if name in packages:return
    packages.add(name)
    for dependency in lock['packages'][name].get('depends',[]):visit(dependency)
for name in ['numpy','matplotlib']:visit(name)
files=['pyodide.mjs','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip']
files += [lock['packages'][name]['file_name'] for name in sorted(packages)]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for name in pool.map(fetch,files):print('Cached',name,flush=True)
for name in packages:
    item=lock['packages'][name]
    digest=hashlib.file_digest((ROOT/item['file_name']).open('rb'),'sha256').hexdigest()
    assert digest==item['sha256'],name+' checksum mismatch'
with zipfile.ZipFile(ROOT/'python_stdlib.zip') as archive:
    assert archive.testzip() is None, 'Python standard library archive is corrupt'
marker=ROOT/'ready.json.part'
marker.write_text(json.dumps({'version':'0.27.7','files':files}))
marker.replace(ROOT/'ready.json')
print('Local Python runtime ready:',len(files),'files;',len(packages),'verified packages.',flush=True)
