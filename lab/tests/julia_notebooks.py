"""Execute representative original notebooks in memory; never overwrite source."""
import os
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
os.environ.update({'JUPYTER_DATA_DIR':str(SITE/'.runtime/jupyter-data'),'JUPYTER_RUNTIME_DIR':str(SITE/'.runtime/jupyter-runtime'),'IPYTHONDIR':str(SITE/'.runtime/ipython')})
import nbformat
from nbclient import NotebookClient
import sys
for name in (sys.argv[1:] or ['Gram-Schmidt.ipynb','QR Factorization Examples in Julia.ipynb','Conditioning.ipynb']):
    path=SITE.parent/'notes'/name
    original=path.read_bytes()
    nb=nbformat.reads(original.decode(),as_version=4)
    client=NotebookClient(nb,kernel_name='julia-1806',timeout=300,startup_timeout=120,resources={'metadata':{'path':str(path.parent)}})
    client.execute()
    assert path.read_bytes()==original,'The original notebook was modified'
    code=[c for c in nb.cells if c.cell_type=='code' and c.source.strip()]
    plots=sum('image/png' in out.get('data',{}) for c in code for out in c.outputs)
    assert all(not any(o.output_type=='error' for o in c.outputs) for c in code)
    if name=='Conditioning.ipynb':assert plots>0
    print(f'{name}: {len(code)} cells passed, {plots} PNG outputs; original unchanged.',flush=True)
