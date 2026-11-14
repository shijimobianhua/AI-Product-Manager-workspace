# -*- coding: utf-8 -*-
"""Maintainer-only inventory refresh; review every included file before publication."""
from pathlib import Path
import os,json,hashlib
ROOT=Path(__file__).resolve().parents[2];cfg=json.loads((ROOT/'workspace.yaml').read_text(encoding='utf-8'))
if cfg.get('project',{}).get('mode')!='template' or cfg.get('components'):raise SystemExit('Refusing to publish an actual product as a generic template')
files={}
for d,dirs,names in os.walk(str(ROOT)):
 dirs[:]=[n for n in dirs if n not in ['.git','node_modules','__pycache__','.venv'] and not (Path(d)==ROOT and n=='outputs')]
 for name in names:
  p=Path(d)/name;relative=p.relative_to(ROOT).as_posix()
  if relative=='00-rules/template-manifest.json':continue
  if p.is_symlink():raise SystemExit('Symlinks are not part of the generic distribution')
  if relative.startswith('10-code/') and relative!='10-code/README.md':raise SystemExit('Business source is not allowed in the generic template')
  files[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'outputs/README.md';files['outputs/README.md']=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'00-rules/template-manifest.json').write_text(json.dumps({'schemaVersion':1,'purpose':'Only these reviewed generic files may be copied by the initializer','files':dict(sorted(files.items()))},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Reviewed template inventory: '+str(len(files))+' files')
