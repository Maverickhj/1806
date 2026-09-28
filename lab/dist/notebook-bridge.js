const byId = id => document.getElementById(id);
let connection = null, ready, frameReady = false;

function message(text) { byId('native-status').textContent = text; }
function hide() { byId('native-workspace').hidden=true; byId('main').hidden=false; }
function openPane() {
  byId('main').hidden = true;
  byId('native-workspace').hidden = false;
  byId('native-back').focus();
}
async function labApp() {
  const deadline = Date.now() + 60000;
  let app;
  while (!(app = byId('native-frame').contentWindow?.jupyterapp)) {
    if (Date.now() > deadline) throw new Error('编辑器仍在加载，请稍候重试。');
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  await app.restored;
  return app;
}
async function command(name) {
  try {
    const app = await labApp();
    if (!app.commands.hasCommand(name)) throw new Error('请先在编辑器中选中一个 notebook。');
    if (!app.commands.isEnabled(name)) throw new Error('请先选中要操作的 notebook 或单元格。');
    await app.commands.execute(name);
    message(name === 'docmanager:save' ? '当前文档已保存到磁盘。' : '已执行操作；结果显示在 notebook 单元格下方。');
  } catch (error) { message(error.message); }
}
function labUrl(file) {
  return connection.lab_url + (file ? '/tree/notes/' + encodeURIComponent(file) : '/tree/notes');
}
async function open(file) {
  await ready;
  openPane();
  if (!connection) {
    message('本地 Jupyter 尚未连接。请通过项目的 start.sh 启动网站，再刷新此页。');
    return;
  }
  if (file && !connection.notebooks.includes(file)) {message('未找到这个原始 notebook，请从列表重新选择。');return;}
  if (file) byId('native-file').value = file;
  byId('native-new-tab').href = labUrl(file);
  const frame = byId('native-frame');
  if (frameReady && file) {
    try {
      const app = await labApp();
      await app.commands.execute('docmanager:open', {path:'notes/'+file, factory:'Notebook'});
      message('正在编辑原项目文件。Ctrl / ⌘ + S 保存；Shift + Enter 运行单元格。');
      return;
    } catch (error) { message(error.message); return; }
  }
  if (!frame.getAttribute('src')) {
    message('正在打开本地 JupyterLab…');
    frame.src = labUrl(file);
  }
}
async function init() {
  byId('open-native').addEventListener('click', () => open(byId('native-file').value));
  byId('native-open').addEventListener('click', () => open(byId('native-file').value));
  byId('native-back').addEventListener('click', () => {hide();byId('open-native').focus();});
  byId('native-save').addEventListener('click', () => command('docmanager:save'));
  byId('native-run').addEventListener('click', () => command('notebook:run-cell'));
  byId('native-interrupt').addEventListener('click', () => command('notebook:interrupt-kernel'));
  byId('native-frame').addEventListener('load', async () => {
    try {
      const app = await labApp();frameReady=true;
      const doc=byId('native-frame').contentDocument;
      if(!doc.querySelector('#course-font')){const link=doc.createElement('link');link.id='course-font';link.rel='stylesheet';link.href='/learn/jupyter-theme.css';doc.head.append(link);}
      for (const id of ['native-save','native-run','native-interrupt']) byId(id).disabled=false;
      message('Jupyter 编辑器已就绪。修改后可保存到原文件；Markdown 单元格也会一起保存。');
    } catch {message('编辑器未能连接。可点击“独立窗口”登录或重新打开。');}
  });
  ready = (async () => {
    try {
      const response=await fetch('/learn-api/status', {headers:{Accept:'application/json'}});
      if(!response.ok || !(response.headers.get('content-type')||'').includes('json'))return;
      const data=await response.json();if(!data.connected)return;connection=data;
      for (const file of data.notebooks) {const option=document.createElement('option');option.value=file;option.textContent=file;byId('native-file').append(option);}
      byId('native-file').value=data.notebooks.includes('Gram-Schmidt.ipynb')?'Gram-Schmidt.ipynb':data.notebooks[0];
      byId('native-count').textContent=`${data.notebooks.length} 个原始文件`;
      byId('native-open').disabled=false;
      byId('native-connection').textContent=data.julia_kernel?'Jupyter · Julia 已连接':'Jupyter 已连接 · Julia 内核未就绪';
      byId('native-new-tab').href=labUrl(byId('native-file').value);
    } catch { /* Static-only mode can still read materials and run browser Python. */ }
  })();
  await ready;
  if(!connection)byId('native-connection').textContent='当前为阅读模式 · 请用 start.sh 启动本地 Jupyter';
}
async function read(file) {
  await ready;
  if(!connection)return null;
  const response=await fetch('/api/contents/notes/'+encodeURIComponent(file)+'?content=1');
  if(!response.ok)throw new Error('无法读取磁盘中的原始文件');
  return (await response.json()).content;
}
export const notebookBridge={init,open,hide,read,isConnected:()=>!!connection,downloadUrl:(file)=>connection?'/files/notes/'+encodeURIComponent(file)+'?download=1':'materials/'+encodeURIComponent(file)};
