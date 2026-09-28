"""Integration checks against the locally served static site."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL=os.environ.get('LAB_URL','http://127.0.0.1:4186/')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(URL)
    page.wait_for_selector('#lesson-nav a')
    assert page.locator('#lesson-nav a').count()==15
    assert page.locator('#lesson-title').inner_text()=='认识你的线性代数计算器'
    for lesson in [f'T{i:02d}' for i in range(14)]+['final']:
        page.locator(f'.nav-item[data-id="{lesson}"]').click()
        page.wait_for_function('(id)=>document.querySelector("#code-filename").textContent===id+".py"',arg=lesson)
        page.locator('#run').click()
        page.wait_for_function('document.querySelector("#run").disabled===false',timeout=180000)
        status=page.locator('#run-time').inner_text()
        if not status.startswith('完成'):
            raise AssertionError(f'{lesson}: {status}\n{page.locator("#output").inner_text()}')
        if lesson in ('T06','T12'): assert page.locator('#output img').count()>0
        print(lesson,'browser Python passed',flush=True)
    # Editing, explicit Python errors, recovery and canceling nonterminating Python.
    page.locator('#code-editor').fill('print(6 * 7)')
    page.locator('#run').click()
    page.wait_for_function('!document.querySelector("#run").disabled',timeout=30000)
    assert page.locator('#output').inner_text().strip()=='42'
    page.locator('#code-editor').fill('raise ValueError("expected-test-error")')
    page.locator('#run').click()
    page.wait_for_function('!document.querySelector("#run").disabled',timeout=30000)
    assert 'expected-test-error' in page.locator('#output').inner_text()
    page.locator('#code-editor').fill('while True:\n    pass')
    page.locator('#run').click()
    page.wait_for_function('document.querySelector("#runtime-status").textContent.includes("正在运行")',timeout=120000)
    page.locator('#stop').click()
    assert page.locator('#run').is_enabled()
    page.locator('#code-editor').fill('print("recovered")')
    page.locator('#run').click()
    page.wait_for_function('!document.querySelector("#run").disabled',timeout=120000)
    assert 'recovered' in page.locator('#output').inner_text()
    print('Edit, error, infinite-loop stop and recovery passed',flush=True)
    # Device-local persistence and exported real ipynb.
    page.locator('#task-list input').first.check()
    page.locator('#notes').fill('我的验收笔记')
    page.locator('#complete').click()
    page.reload();page.wait_for_selector('#lesson-nav a')
    assert page.locator('#notes').input_value()=='我的验收笔记'
    assert page.locator('#code-editor').input_value()=='print("recovered")'
    assert page.locator('#task-list input').first.is_checked()
    with page.expect_download() as download:
        page.locator('#download').click()
    nb=json.loads(Path(download.value.path()).read_text())
    assert nb['nbformat']==4 and 'recovered' in ''.join(nb['cells'][1]['source'])
    # Original notebook rendering, reset confirmation, desktop and mobile overflow.
    page.locator('.nav-item[data-id="T00"]').click()
    page.locator('#tab-materials').click()
    page.locator('.material-card').first.click()
    page.wait_for_selector('#notebook-reader .reader-header')
    assert page.locator('#notebook-reader pre').count()>0
    page.locator('#tab-learn').click()
    page.locator('#code-editor').fill('print("changed")')
    page.locator('#reset-code').click()
    page.locator('#cancel-reset').click()
    assert page.locator('#code-editor').input_value()=='print("changed")'
    page.locator('#reset-code').click();page.locator('#confirm-reset-button').click()
    assert 'import numpy' in page.locator('#code-editor').input_value()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path='/tmp/1806-desktop.png',full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('#menu').click();page.locator('.nav-item[data-id="T12"]').click()
    assert not page.locator('body').evaluate('(e)=>e.classList.contains("menu-open")')
    page.screenshot(path='/tmp/1806-mobile.png',full_page=True)
    print('Persistence, download, notebook reading, reset and responsive checks passed',flush=True)
    # Feature-detected tools: verify registration contract and execute using an API harness.
    probe=browser.new_page()
    probe.add_init_script('window.registeredTools={};document.modelContext={registerTool:(tool)=>{window.registeredTools[tool.name]=tool;}}')
    probe.goto(URL);probe.wait_for_function('!!window.registeredTools.navigate_to_lesson')
    result=probe.evaluate('async()=>await window.registeredTools.navigate_to_lesson.execute({id:"T05"})')
    assert result['id']=='T05'
    data=probe.evaluate('async()=>await window.registeredTools.read_current_lesson.execute({})')
    assert data['id']=='T05'
    invalid=probe.evaluate('async()=>{try{await window.registeredTools.navigate_to_lesson.execute({id:"bad"});return false}catch{return true}}')
    assert invalid and probe.locator('#code-filename').inner_text()=='T05.py'
    print('WebMCP API harness passed (native supported host not available)',flush=True)
    assert not errors,errors
    browser.close()
