import json, re, shutil
from pathlib import Path
from urllib.parse import unquote
from lessons import LESSONS, CAPSTONE

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent
DIST=ROOT/'dist'
roadmap=(SOURCE/'action-roadmap.md').read_text()
readme=(SOURCE/'README.md').read_text()
parts=re.split(r'^### T\d{2} · .*\n',roadmap,flags=re.M)[1:]
parts[-1]=parts[-1].split('\n## 4.')[0]
lecture_parts=re.split(r'^### Lecture (\d+) ([^\n]+)\n',readme,flags=re.M)
lectures={}
for i in range(1,len(lecture_parts),3):
    body=lecture_parts[i+2].split('\n### Exam')[0].strip().strip('-').strip()
    lectures[int(lecture_parts[i])]=body
(DIST/'materials').mkdir(exist_ok=True)
(DIST/'downloads').mkdir(exist_ok=True)
# Retain every original notebook for reading and downloading; never execute Julia as Python.
for p in (SOURCE/'notes').iterdir():
    if p.suffix in ('.ipynb','.png','.jpg','.pdf'):
        shutil.copy2(p,DIST/'materials'/p.name)
shutil.copy2(SOURCE/'action-roadmap.md',DIST/'downloads/action-roadmap.md')
shutil.copy2(SOURCE/'learning-roadmap.md',DIST/'downloads/learning-roadmap.md')

def material_links(body):
    return [{'name':label,'file':unquote(url.removeprefix('notes/'))} for label,url in re.findall(r'\[([^\]]+)\]\((notes/[^)]+)\)',body)]

all_lessons=[]
for i,item in enumerate(LESSONS+[CAPSTONE]):
    d=dict(item);d['id']=f'T{i:02d}' if i<14 else 'final'
    d['number']=f'{i:02d}' if i<14 else '✓'
    body=parts[i] if i<14 else roadmap.split('## 4. 最终验收：用一张矩阵串起主线')[1].split('## 5.')[0]
    d['tasks']=re.findall(r'^- \[ \] (.+)$',body,flags=re.M)
    d['detail']=body
    d['materials']=material_links(body)
    if i==0:d['materials']=[{'name':'矩阵乘法的多个视角','file':'Matrix-mult-perspectives.ipynb'}]
    d['lectureText']='\n\n'.join(f'## Lecture {n}\n\n{lectures[n]}' for n in item['lectures'])
    d['duration']='60–90 分钟' if i<14 else '30–45 分钟'
    all_lessons.append(d)
(DIST/'content.json').write_text(json.dumps({'lessons':all_lessons,'corrections':roadmap.split('## 6.')[1],'overview':roadmap.split('## 3.')[0]},ensure_ascii=False))
print(f'Generated {len(all_lessons)} lessons, {len(lectures)} lecture summaries.')
