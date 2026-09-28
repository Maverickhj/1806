"""Exercise edit/run/save/reopen through the embedded, authenticated Jupyter UI."""
import json, os, urllib.request, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
SITE=Path(__file__).resolve().parents[1]
BASE=os.environ.get('LAB_BASE','http://127.0.0.1:4188')
token=(SITE/'.runtime/jupyter-token').read_text().strip()
name='__integration_'+uuid.uuid4().hex[:10]+'.ipynb'
path=SITE.parent/'notes'/name
original=SITE.parent/'notes/Gram-Schmidt.ipynb'
original_bytes=original.read_bytes()
nb=json.loads(original_bytes)
nb['metadata']['kernelspec']={'name':'julia-1806','display_name':'Julia 18.06','language':'julia'}
nb['nbformat_minor']=5
nb['cells']=[{'cell_type':'markdown','id':'explanation','source':['# Integration check\n\nTemporary notebook; removed after validation.'],'metadata':{}},{'cell_type':'code','id':'editable','source':['1+1'],'metadata':{},'outputs':[],'execution_count':None}]
path.write_text(json.dumps(nb))
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def api(method,endpoint,body=None):
    req=urllib.request.Request(BASE+endpoint,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Authorization':'token '+token,'Content-Type':'application/json'})
    with opener.open(req,timeout=30) as response:return json.loads(response.read() or b'null')
existing_sessions={session['id'] for session in api('GET','/api/sessions')}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1540,'height':1050},reduced_motion='reduce')
        # Keep test tabs separate from the user's persisted Jupyter workspace.
        def isolated_workspace(route):
            response=route.fetch()
            status=response.json()
            status['lab_url']='/lab/workspaces/'+name.removesuffix('.ipynb')
            route.fulfill(response=response,json=status)
        page.route('**/learn-api/status',isolated_workspace)
        page.goto(BASE+'/learn/?token='+token)
        page.wait_for_function('document.querySelector("#native-file").options.length>0')
        page.select_option('#native-file',name,force=True)
        page.click('#open-native')
        page.wait_for_function('!document.querySelector("#native-save").disabled',timeout=120000)
        frame=page.frame_locator('#native-frame')
        page.wait_for_function('document.querySelector("#native-frame").contentWindow.jupyterapp.shell.currentWidget?.context?.path?.includes("__integration_")',timeout=120000)
        page.evaluate('async()=>{const w=document.querySelector("#native-frame").contentWindow.jupyterapp.shell.currentWidget;await w.context.ready;await w.sessionContext.ready;}')
        print('Embedded notebook opened with live Julia kernel.',flush=True)
        editor=frame.locator('.jp-NotebookPanel:visible .jp-Notebook .jp-CodeCell .cm-content').last
        code='using LinearAlgebra\nA = [2.0 1.0; 1.0 3.0]\nb = [1.0, 2.0]\nprintln("NATIVE-JULIA-OK ", A \\ b)'
        editor.click()
        editor.fill(code)
        page.click('#native-run')
        print('Run status:',page.locator('#native-status').inner_text(),flush=True)
        page.wait_for_function('''()=>{const w=document.querySelector('#native-frame').contentWindow.jupyterapp.shell.currentWidget;return w.content.model.sharedModel.getCell(1).getOutputs().some(o=>JSON.stringify(o).includes('NATIVE-JULIA-OK'));}''',timeout=60000)
        print('Edited Julia code ran through the website control.',flush=True)
        # Save a Markdown summary in the real notebook model, through Jupyter's save command.
        page.evaluate("""(source)=>{const app=document.querySelector('#native-frame').contentWindow.jupyterapp;const w=app.shell.currentWidget;w.content.model.sharedModel.insertCell(2,{cell_type:'markdown',source,metadata:{}});}""", "## 学习总结\n\n已验证 Julia 计算和本地文件持久化。")
        page.click('#native-save')
        page.wait_for_function('document.querySelector("#native-status").textContent.includes("已保存到磁盘")')
        saved=json.loads(path.read_text())
        assert ''.join(saved['cells'][1]['source'])==code
        assert any('NATIVE-JULIA-OK' in ''.join(o.get('text',[])) for o in saved['cells'][1]['outputs'])
        assert '学习总结' in ''.join(saved['cells'][2]['source'])
        print('Code, output and Markdown summary saved to the actual ipynb on disk.',flush=True)
        # Reload the whole page and verify the notebook can read back the saved source.
        page.reload();page.wait_for_function('document.querySelector("#native-file").options.length>0')
        page.select_option('#native-file',name,force=True);page.click('#open-native')
        page.wait_for_function('!document.querySelector("#native-save").disabled',timeout=120000)
        frame=page.frame_locator('#native-frame')
        frame.get_by_text('已验证 Julia 计算和本地文件持久化。',exact=False).last.wait_for(timeout=60000)
        # A later command opens another notebook without discarding unsaved tabs.
        page.select_option('#native-file','Gram-Schmidt.ipynb');page.click('#native-open')
        page.wait_for_function('document.querySelector("#native-frame").contentWindow.jupyterapp.shell.currentWidget?.context?.path==="notes/Gram-Schmidt.ipynb"',timeout=90000)
        assert original.read_bytes()==original_bytes
        page.locator('#native-back').click()
        assert page.locator('#main').is_visible()
        page.locator('#open-native').click()
        assert page.locator('#native-frame').is_visible()
        page.screenshot(path='/tmp/1806-jupyter-ready.png',full_page=True)
        print('Reload, navigation and original-file preservation passed.',flush=True)
        browser.close()
finally:
    # Shut down only sessions created for these specific validation documents.
    for session in api('GET','/api/sessions'):
        if session['id'] not in existing_sessions and session.get('path') in ('notes/'+name,'notes/Gram-Schmidt.ipynb'):
            api('DELETE','/api/sessions/'+session['id'])
    if path.exists():path.unlink()
    checkpoints=path.parent/'.ipynb_checkpoints'
    for checkpoint in checkpoints.glob(path.stem+'-checkpoint.ipynb') if checkpoints.exists() else []:checkpoint.unlink()
