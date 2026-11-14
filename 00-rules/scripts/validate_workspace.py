# -*- coding: utf-8 -*-
"""Validate structure and references; never approves requirements or deploys."""
from pathlib import Path
import argparse,json,re,os,subprocess,struct
from urllib.parse import unquote
from workspace_core import ROOT,read_config,STATES,within
SKIP={'.git','node_modules','__pycache__','.venv','checkpoints'}
def validate(root):
 root=root.resolve();errors=[];files=[]
 try:cfg=read_config(root)
 except (ValueError,OSError) as e:return [str(e)]
 try:directory_map=json.loads((root/'00-rules/directory-map.json').read_text(encoding='utf-8'))['directories']
 except (ValueError,OSError,KeyError) as e:return ['Missing directory map: '+str(e)]
 for entry in directory_map:
  folder=within(root,entry['path']);readme=folder/'README.md';image=root/'90-assets/diagrams'/(entry['diagram']+'.png')
  if not readme.is_file():errors.append('Missing directory guide: '+entry['path'])
  elif '![' not in readme.read_text(encoding='utf-8'):errors.append('Folder guide lacks its illustration: '+entry['path'])
  if not image.is_file():errors.append('Missing folder image: '+entry['path'])
  else:
   data=image.read_bytes()
   if data[:8]!=b'\x89PNG\r\n\x1a\n' or len(data)<24:errors.append('Invalid PNG: '+image.name)
   else:
    w,h=struct.unpack('>II',data[16:24])
    if w<1000 or h<600:errors.append('Folder image too small: '+image.name)
 for d,dirs,names in os.walk(str(root)):
  dirs[:]=[x for x in dirs if x not in SKIP and not (Path(d)==root and x=='outputs')]
  for name in names:
   file=Path(d)/name
   if file.is_symlink():errors.append('Unexpected symlink in shared template: '+str(file.relative_to(root)));continue
   files.append(file)
 output_guide=root/'outputs/README.md'
 if output_guide.is_file():files.append(output_guide)
 for file in files:
  if file.suffix!='.md':continue
  try:text=file.read_text(encoding='utf-8')
  except UnicodeError:errors.append('Invalid UTF-8: '+str(file.relative_to(root)));continue
  for raw in re.findall(r'\]\(([^)]+)\)',text):
   if re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#)',raw):continue
   relative=unquote(raw.split('#')[0]);target=(file.parent/relative).resolve()
   if target!=root and root not in target.parents:errors.append('Link leaves workspace: '+str(file.relative_to(root)))
   elif not target.exists():errors.append('Broken link: '+str(file.relative_to(root))+' -> '+raw)
 for item in cfg['components']:
  source=within(root,item['source'])
  if not source.is_dir():errors.append('Component source does not exist: '+item['id'])
  if (source/'.git').exists():errors.append('Nested component Git requires an explicit design: '+item['id'])
 sources=(root/'01-inputs/source-register.md').read_text(encoding='utf-8');source_ids=set(re.findall(r'^\|\s*(SRC-\d{4})\s*\|',sources,re.M));pool=(root/'04-requirement-pool/requirement-pool.md').read_text(encoding='utf-8');req_ids=[]
 for line in pool.splitlines():
  if not re.match(r'^\|\s*REQ-\d{4}\s*\|',line):continue
  cells=[x.strip() for x in line.strip('|').split('|')]
  if len(cells)!=10:errors.append('Requirement row needs ten fields');continue
  req_ids.append(cells[0])
  if cells[4] not in STATES:errors.append('Unknown requirement state: '+cells[0])
  for source in re.findall(r'SRC-\d{4}',cells[2]):
   if source not in source_ids:errors.append('Missing requirement source: '+source)
  if not re.search(r'SRC-\d{4}',cells[2]):errors.append('Requirement lacks a source: '+cells[0])
 if len(req_ids)!=len(set(req_ids)):errors.append('Duplicate requirement IDs')
 if (root/'.git').exists():
  tracked=subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode('utf-8').rstrip('\0').split('\0')
  for name in tracked:
   if name.startswith('outputs/') and name!='outputs/README.md':errors.append('Generated output is tracked: '+name)
   if '/node_modules/' in '/'+name or Path(name).name in ['.env','auth.json'] or name.endswith(('.p12','.pfx','.jks','.keystore','.sqlite','.bundle')):errors.append('Private or derived file tracked: '+name)
 return errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);args=p.parse_args();errors=validate(args.root);print(json.dumps({'ok':not errors,'errors':errors,'scope':'structure, illustrations, links, registry boundaries; not business acceptance'},ensure_ascii=True));raise SystemExit(1 if errors else 0)
