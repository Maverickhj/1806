import { notebookBridge } from './notebook-bridge.js';
const $ = (id) => document.getElementById(id);
const STORAGE = 'linear-algebra-lab-v1';
let course, current, worker, running = false, activeTab = 'learn', readerRequest = 0;
let runOwner = null, watchdog, state = { lessons: {}, last: 'T00' };
let storageAvailable = true;
try { const saved = JSON.parse(localStorage.getItem(STORAGE)); if (saved && typeof saved === 'object' && saved.lessons && typeof saved.lessons === 'object') state = saved; } catch { storageAvailable = false; }
function save() {
  try { localStorage.setItem(STORAGE, JSON.stringify(state)); storageAvailable = true; $('save-status').textContent = '代码与笔记已自动保存'; }
  catch { storageAvailable = false; $('save-status').textContent = '浏览器无法保存，请下载 notebook 留存'; }
}
function record(id = current.id) {
  if (!state.lessons[id] || typeof state.lessons[id] !== 'object') state.lessons[id] = {};
  const rec = state.lessons[id];
  if (!Array.isArray(rec.checked)) rec.checked = [];
  return rec;
}
function escapeHtml(text) { const span = document.createElement('span'); span.textContent = text; return span.innerHTML; }
function renderMarkdown(text, target) {
  // Protect TeX delimiters while Markdown parses, then restore for KaTeX.
  const math = [];
  let source = text.replace(/\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\$)\$(?!\$)[^\n$]+\$(?!\$)/g, (s) => { math.push(s); return `MATHPLACEHOLDER${math.length-1}END`; });
  let html = marked.parse(source);
  html = html.replace(/MATHPLACEHOLDER(\d+)END/g, (_, i) => escapeHtml(math[Number(i)]));
  target.innerHTML = DOMPurify.sanitize(html, { ADD_ATTR: ['target'] });
  target.querySelectorAll('a').forEach((a) => {
    const href = a.getAttribute('href') || '';
    if (href.startsWith('notes/')) {
      const file = decodeURIComponent(href.slice(6));
      if (file.endsWith('.ipynb')) { a.href = '#materials'; a.addEventListener('click', (e) => { e.preventDefault(); setTab('materials'); readNotebook(file, a.textContent); }); }
      else a.href = 'materials/' + encodeURIComponent(file);
    } else if (href === 'README.md') {
      a.href = '#lecture'; a.addEventListener('click', e => {e.preventDefault(); setTab('materials'); $('lecture-content').parentElement.open = true; $('lecture-content').scrollIntoView({block:'start'});});
    } else if (href.endsWith('learning-roadmap.md')) a.href = 'downloads/learning-roadmap.md';
    else if (href.endsWith('action-roadmap.md')) a.href = 'downloads/action-roadmap.md';
    else if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
  });
  target.querySelectorAll('img').forEach(img => { const src=img.getAttribute('src') || ''; if (!/^(?:https?:|data:|\/)/.test(src)) img.src='materials/'+src; img.loading='lazy'; });
  window.renderMathInElement?.(target, { delimiters: [{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false},{left:'$',right:'$',display:false}], throwOnError:false, strict:false });
}
function inline(text) { return DOMPurify.sanitize(marked.parseInline(text)); }
function updateProgress() {
  const count = course.lessons.slice(0,14).filter(l => record(l.id).complete).length;
  $('progress').value = count; $('progress-text').textContent = `${count} / 14 次完成`; $('progress-percent').textContent = Math.round(count/14*100)+'%';
  document.querySelectorAll('.nav-item').forEach(el => {const rec=record(el.dataset.id);el.classList.toggle('done',!!rec.complete);el.querySelector('.nav-num').textContent=rec.complete?'✓':course.lessons.find(l=>l.id===el.dataset.id).number;});
}
function buildNav() {
  let group = '';
  $('lesson-nav').replaceChildren();
  for (const lesson of course.lessons) {
    if (lesson.group !== group) {group=lesson.group;const header=document.createElement('div');header.className='nav-group';header.textContent=group;$('lesson-nav').append(header);}
    const a=document.createElement('a');a.href='#'+lesson.id;a.className='nav-item';a.dataset.id=lesson.id;
    a.innerHTML=`<span class="nav-num">${lesson.number}</span><span>${escapeHtml(lesson.short)}</span>`;
    a.addEventListener('click',()=>{document.body.classList.remove('menu-open');$('menu').setAttribute('aria-expanded','false');});
    $('lesson-nav').append(a);
  }
}
function setTab(tab) {
  activeTab=tab;
  for (const key of ['learn','materials']) {const selected=key===tab;$('tab-'+key).setAttribute('aria-selected',String(selected));$('tab-'+key).tabIndex=selected?0:-1;$('panel-'+key).hidden=!selected;}
}
function updateLines() {$('line-numbers').textContent=Array.from({length:$('code-editor').value.split('\n').length},(_,i)=>i+1).join('\n');$('line-numbers').scrollTop=$('code-editor').scrollTop;}
function updateTaskCount() {const checked=record().checked.filter((v,i)=>v&&i<current.tasks.length).length;$('task-count').textContent=`${checked} / ${current.tasks.length} 项`;}
function updateComplete() {const done=!!record().complete;$('complete').textContent=done?'✓ 已掌握 · 点击撤销':'我已掌握本次内容';$('complete').setAttribute('aria-pressed',String(done));updateProgress();}
function selectLesson(id, focus=false) {
  notebookBridge.hide();
  const next=course.lessons.find(l=>l.id===id) || course.lessons[0];
  if (running) stopRun('已切换任务，上一段运行已停止。');
  current=next;readerRequest++;const rec=record();state.last=current.id;save();
  document.title=`${current.id==='final'?'综合验收':current.id} · ${current.short} | 18.06 学习室`;
  $('lesson-id').textContent=current.id==='final'?'综合验收':current.id;$('group-name').textContent=current.group;$('duration').textContent=current.duration;
  $('lesson-title').textContent=current.title;$('lesson-lead').textContent=current.lead;
  katex.render(current.formula,$('formula'),{displayMode:true,throwOnError:false});
  renderMarkdown(current.concept,$('concept-text'));$('challenge-text').textContent=current.challenge;
  $('task-list').replaceChildren();current.tasks.forEach((text,i)=>{const label=document.createElement('label');label.className='task'+(rec.checked[i]?' checked':'');const input=document.createElement('input');input.type='checkbox';input.checked=!!rec.checked[i];input.addEventListener('change',()=>{record().checked[i]=input.checked;label.classList.toggle('checked',input.checked);save();updateTaskCount();});const span=document.createElement('span');span.innerHTML=inline(text);label.append(input,span);$('task-list').append(label);});
  renderMarkdown(current.detail,$('lesson-detail'));$('lesson-detail').querySelectorAll('input').forEach(input=>input.disabled=true);
  $('notes').value=typeof rec.notes==='string'?rec.notes:'';$('code-editor').value=typeof rec.code==='string'?rec.code:current.code;$('code-filename').textContent=current.id+'.py';updateLines();
  $('output').innerHTML='<div class="empty-output"><span>[ ]</span><p>先预测，再验证。</p><small>修改上方代码，点击「运行代码」查看真实结果。</small></div>';
  $('run-time').textContent='尚未运行';$('material-count').textContent=current.materials.length+ (current.lectures.length?1:0);
  $('material-list').replaceChildren();current.materials.forEach(material=>{const button=document.createElement('button');button.className='material-card';button.innerHTML=`${escapeHtml(material.name)} ↗<small>${escapeHtml(material.file)} · Julia 原材料</small>`;button.addEventListener('click',()=>readNotebook(material.file,material.name));$('material-list').append(button);});
  renderMarkdown(current.lectureText||'本次使用路线中的补充材料与练习，没有单独对应的课程讲次。',$('lecture-content'));
  $('notebook-reader').replaceChildren();updateTaskCount();updateComplete();
  const idx=course.lessons.indexOf(current);$('next').disabled=idx===course.lessons.length-1;$('next').textContent=idx===13?'综合验收 →':'下一次 →';
  document.querySelectorAll('.nav-item').forEach(a=>{if(a.dataset.id===current.id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
  setTab('learn');if(focus){$('lesson-title').focus({preventScroll:true});window.scrollTo({top:0});}
}
async function readNotebook(file, title) {
  if (!file.endsWith('.ipynb')) {window.open('materials/'+encodeURIComponent(file),'_blank','noopener');return;}
  const token=++readerRequest;
  $('notebook-reader').textContent='正在加载原始 notebook…';
  try {
    let nb=await notebookBridge.read(file);
    if(!nb){const response=await fetch('materials/'+encodeURIComponent(file));if(!response.ok)throw new Error('无法读取此材料');nb=await response.json();}
    if(token!==readerRequest)return;
    const target=$('notebook-reader');target.replaceChildren();const header=document.createElement('div');header.className='reader-header';header.innerHTML=`<strong>${escapeHtml(title)}</strong><a download href="${notebookBridge.downloadUrl(file)}">下载原始 Julia notebook</a>`;const edit=document.createElement('button');edit.className='primary';edit.textContent='编辑并运行原文件';edit.addEventListener('click',()=>notebookBridge.open(file));header.append(edit);target.append(header);
    const notice=document.createElement('p');notice.className='material-note';notice.textContent='此处为阅读视图；点击“编辑并运行原文件”可修改单元格、运行 Julia 并保存回磁盘。';target.append(notice);
    for(const cell of nb.cells||[]) {
      const section=document.createElement('section');const src=Array.isArray(cell.source)?cell.source.join(''):cell.source||'';
      if(cell.cell_type==='markdown')renderMarkdown(src,section);
      else if(cell.cell_type==='code') {
        const label=document.createElement('div');label.className='nb-code-label';label.textContent='JULIA · 原始示例';const pre=document.createElement('pre');pre.textContent=src;section.append(label,pre);
        for(const output of cell.outputs||[]) {
          const data=output.data||{};
          if(data['image/png']){const img=document.createElement('img');img.src='data:image/png;base64,'+(Array.isArray(data['image/png'])?data['image/png'].join(''):data['image/png']);img.alt='原 notebook 保存的图像输出';img.loading='lazy';section.append(img);}
          else if(output.text||data['text/plain']){const pre=document.createElement('pre');const text=output.text||data['text/plain'];pre.textContent=Array.isArray(text)?text.join(''):text;section.append(pre);}
          else if(data['text/html']){const out=document.createElement('div');out.className='nb-output';out.innerHTML=DOMPurify.sanitize(Array.isArray(data['text/html'])?data['text/html'].join(''):data['text/html'],{FORBID_TAGS:['iframe','script','style'],FORBID_ATTR:['style']});section.append(out);}
        }
      }
      target.append(section);
    }
    target.scrollIntoView({block:'start'});
  }catch(error){if(token===readerRequest)$('notebook-reader').textContent=error.message+'，请稍后重试。';}
}
function appendOutput(text,error=false) {const pre=document.createElement('pre');pre.textContent=String(text);if(error)pre.className='error';$('output').append(pre);}
function setRunning(value){running=value;$('run').disabled=value;$('stop').disabled=!value;$('run').innerHTML=value?'运行中…':'<span aria-hidden="true">▷</span> 运行代码';}
function endRun(){clearTimeout(watchdog);setRunning(false);runOwner=null;}
function stopRun(message='运行已停止。再次运行会重新加载环境。') {worker?.terminate();worker=null;endRun();$('runtime-status').textContent='已停止 · 可重新运行';$('run-time').textContent='已停止';appendOutput(message);$('run-announcement').textContent=message;}
function runCode() {
  if(running||!current)return;
  const code=$('code-editor').value;record().code=code;save();setRunning(true);$('output').replaceChildren();$('run-time').textContent='正在准备…';runOwner=current.id;
  $('runtime-status').textContent=worker?'正在准备执行…':'正在加载 Python…';
  if(!worker){worker=new Worker('python-worker.js',{type:'module'});worker.onmessage=({data})=>{
    if(!running||runOwner!==current.id)return;
    if(data.type==='status'){$('runtime-status').textContent=data.text;}
    else if(data.type==='stdout'||data.type==='stderr')appendOutput(data.text,data.type==='stderr');
    else if(data.type==='plot'){const img=document.createElement('img');img.src='data:image/png;base64,'+data.png;img.alt='当前 Python 代码生成的图表';$('output').append(img);}
    else if(data.type==='done'){$('run-time').textContent=`完成 · ${data.seconds.toFixed(2)} s`;$('runtime-status').textContent='Python 已就绪 · NumPy 可用';if(!$('output').childElementCount)appendOutput('运行完成，没有输出。可使用 print(...) 查看结果。');$('run-announcement').textContent='Python 运行完成';endRun();}
    else if(data.type==='error'){appendOutput(data.text,true);$('run-time').textContent='运行出错';$('runtime-status').textContent='请检查代码；加载失败时可再次运行';$('run-announcement').textContent='运行出错，请查看输出区域';worker?.terminate();worker=null;endRun();}
  };worker.onerror=(event)=>{appendOutput('Python 环境加载失败。请检查网络后重试。\n'+(event.message||''),true);worker?.terminate();worker=null;$('runtime-status').textContent='环境未就绪 · 可重试';$('run-time').textContent='加载失败';endRun();};}
  watchdog=setTimeout(()=>stopRun('本次运行超过 180 秒，已停止。可减少计算量后重试；首次加载也可能因网络较慢超时。'),180000);
  worker.postMessage({type:'run',code,filename:current.id+'.py'});
}
function downloadNotebook(){
  const source=(text)=>text.split(/(?<=\n)/);
  const nb={nbformat:4,nbformat_minor:5,metadata:{kernelspec:{display_name:'Python 3',language:'python',name:'python3'},language_info:{name:'python'}},cells:[{id:'intro',cell_type:'markdown',metadata:{},source:source(`# ${current.id} · ${current.title}\n\n${current.lead}\n\n${current.concept}\n\n$$${current.formula}$$\n\n${current.detail}`)},{id:'experiment',cell_type:'code',metadata:{},execution_count:null,outputs:[],source:source($('code-editor').value)},{id:'notes',cell_type:'markdown',metadata:{},source:source('## 我的理解与问题\n\n'+$('notes').value)}]};
  const url=URL.createObjectURL(new Blob([JSON.stringify(nb,null,2)],{type:'application/x-ipynb+json'}));const a=document.createElement('a');a.href=url;a.download=`1806-${current.id}.ipynb`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function registerAgentTools(){
  const context=document.modelContext;if(!context?.registerTool)return;
  const controller=new AbortController();window.addEventListener('pagehide',()=>controller.abort(),{once:true});
  const tools=[{name:'read_current_lesson',description:'读取当前任务、学习清单和编辑器内容，不运行代码。',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:true},execute:async()=>({id:current.id,title:current.title,tasks:current.tasks,code:$('code-editor').value,checked:record().checked})},{name:'navigate_to_lesson',description:'切换到指定学习任务；若有代码正在执行，会先停止它。',inputSchema:{type:'object',properties:{id:{type:'string',enum:course.lessons.map(l=>l.id)}},required:['id'],additionalProperties:false},annotations:{readOnlyHint:false},execute:async(input)=>{if(!input||!course.lessons.some(l=>l.id===input.id))throw new Error('无效任务编号');history.replaceState(null,'','#'+input.id);selectLesson(input.id,true);return{id:current.id,title:current.title};}}];
  for(const tool of tools){try{Promise.resolve(context.registerTool(tool,{signal:controller.signal})).catch(()=>{});}catch{}}
}
async function init(){
  try {
    // Classic deferred rendering dependencies must be ready before using them.
    if(document.readyState==='loading')await new Promise(resolve=>document.addEventListener('DOMContentLoaded',resolve,{once:true}));
    if(!window.marked||!window.DOMPurify||!window.katex)throw new Error('页面组件未能加载，请刷新重试。');
    const response=await fetch('content.json');if(!response.ok)throw new Error('课程内容加载失败');course=await response.json();buildNav();renderMarkdown(course.corrections,$('corrections'));
    selectLesson(location.hash.slice(1)||state.last);if(!storageAvailable)$('save-status').textContent='浏览器无法保存，请下载 notebook 留存';
    window.addEventListener('hashchange',()=>selectLesson(location.hash.slice(1),true));
    $('code-editor').addEventListener('input',()=>{record().code=$('code-editor').value;updateLines();save();});$('code-editor').addEventListener('scroll',()=>{$('line-numbers').scrollTop=$('code-editor').scrollTop;});
    $('code-editor').addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();runCode();}else if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();const el=e.target;el.setRangeText('    ',el.selectionStart,el.selectionEnd,'end');el.dispatchEvent(new Event('input'));}});
    $('notes').addEventListener('input',()=>{record().notes=$('notes').value;save();});
    $('tabs').addEventListener('click',e=>{const b=e.target.closest('[data-tab]');if(b)setTab(b.dataset.tab);});
    $('tabs').addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();setTab(e.key==='Home'?'learn':e.key==='End'?'materials':activeTab==='learn'?'materials':'learn');$('tab-'+activeTab).focus();}});
    $('complete').addEventListener('click',()=>{record().complete=!record().complete;save();updateComplete();});
    $('next').addEventListener('click',()=>{const next=course.lessons[course.lessons.indexOf(current)+1];if(next)location.hash=next.id;});
    $('run').addEventListener('click',runCode);$('stop').addEventListener('click',()=>stopRun());$('download').addEventListener('click',downloadNotebook);
    $('reset-code').addEventListener('click',()=>$('confirm-reset').showModal());$('cancel-reset').addEventListener('click',()=>$('confirm-reset').close());$('confirm-reset-button').addEventListener('click',()=>{if(running)stopRun();$('code-editor').value=current.code;record().code=current.code;save();updateLines();$('confirm-reset').close();});
    $('menu').addEventListener('click',()=>{$('menu').setAttribute('aria-expanded',String(document.body.classList.toggle('menu-open')));});
    document.addEventListener('click',e=>{if(document.body.classList.contains('menu-open')&&!e.target.closest('#sidebar')&&!e.target.closest('#menu')){document.body.classList.remove('menu-open');$('menu').setAttribute('aria-expanded','false');}});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.body.classList.remove('menu-open');$('menu').setAttribute('aria-expanded','false');}});
    notebookBridge.init();
    registerAgentTools();
  }catch(error){$('lesson-title').textContent='暂时无法打开学习内容';$('lesson-lead').textContent=error.message+' 请刷新页面重试。';$('run').disabled=true;}
}
init();
