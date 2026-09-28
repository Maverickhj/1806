// Python lives in a dedicated worker so a long-running cell cannot freeze the UI.
const REMOTE_BASE = 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/';
const LOCAL_BASE = new URL('python-runtime/', self.location.href).href;
let pyodide;
let messageCount = 0;
function emit(type, data = {}) { self.postMessage({ type, ...data }); }
function stream(type, text) {
  if (messageCount++ < 1000) emit(type, { text });
  else if (messageCount === 1001) emit('stderr', { text: '输出过多，已截断。可以点击停止。' });
}
self.onmessage = async ({ data }) => {
  if (data.type !== 'run') return;
  messageCount = 0;
  let globals;
  try {
    if (!pyodide) {
      emit('status', { text: '正在加载 Python 环境…' });
      const local = await fetch(LOCAL_BASE + 'ready.json', {cache:'no-store'}).then(async r=>r.ok && (await r.json()).version === '0.27.7').catch(()=>false);
      const BASE = local ? LOCAL_BASE : REMOTE_BASE;
      const { loadPyodide } = await import(BASE + 'pyodide.mjs');
      pyodide = await loadPyodide({ indexURL: BASE, stdout: () => {}, stderr: () => {} });
      emit('status', { text: '正在加载 NumPy…' });
      await pyodide.loadPackage('numpy');
      pyodide.setStdin({ error: true });
    }
    emit('status', { text: '正在准备代码所需的库…' });
    await pyodide.loadPackagesFromImports(data.code, { messageCallback: () => {}, errorCallback: (text) => stream('stderr', text) });
    pyodide.setStdout({ batched: (text) => stream('stdout', text) });
    pyodide.setStderr({ batched: (text) => stream('stderr', text) });
    // Fresh user namespace each time; packages remain cached between runs.
    const dict = pyodide.globals.get('dict');
    globals = dict(); dict.destroy();
    const plots = [];
    globals.set('_site_send_plot', (png) => plots.length < 12 && plots.push(png));
    const hasPlots = pyodide.runPython("'matplotlib' in __import__('sys').modules") || /(?:^|\n)\s*(?:from\s+matplotlib|import\s+matplotlib)/.test(data.code);
    if (hasPlots) {
      await pyodide.runPythonAsync(`import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as _site_plt
import io as _site_io
import base64 as _site_base64
_site_plt.close('all')
def _site_capture(*args, **kwargs):
    for _site_num in _site_plt.get_fignums():
        _site_buf = _site_io.BytesIO()
        _site_plt.figure(_site_num).savefig(_site_buf, format='png', dpi=120, bbox_inches='tight')
        _site_send_plot(_site_base64.b64encode(_site_buf.getvalue()).decode())
    _site_plt.close('all')
_site_plt.show = _site_capture`, { globals });
    }
    emit('status', { text: 'Python 已就绪 · 正在运行' });
    const start = performance.now();
    const result = await pyodide.runPythonAsync(data.code, { globals, filename: data.filename || 'lesson.py' });
    if (result !== undefined && result !== null) { stream('stdout', String(result)); result?.destroy?.(); }
    if (hasPlots) await pyodide.runPythonAsync('_site_capture()', { globals });
    for (const png of plots) emit('plot', { png });
    emit('done', { seconds: (performance.now()-start)/1000 });
  } catch (error) {
    emit('error', { text: String(error.message || error) });
  } finally {
    globals?.destroy();
  }
};
