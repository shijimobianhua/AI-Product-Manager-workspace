"""Pure standard-library helpers for the generic template."""
import json,re,subprocess,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STATES={'candidate','collecting','analyzing','defined','reviewing','approved','developing','validating','released','closed'}
def within(root,relative):
 p=(root/relative).resolve()
 if p!=root.resolve() and root.resolve() not in p.parents:raise ValueError('Path leaves the selected workspace')
 return p
def read_config(root):
 data=json.loads((root/'workspace.yaml').read_text(encoding='utf-8'))
 if data.get('schemaVersion')!=1 or not isinstance(data.get('components'),list):raise ValueError('Invalid workspace schema')
 ids=[]
 for item in data['components']:
  id=item.get('id','')
  if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',id):raise ValueError('Invalid component ID')
  ids.append(id);source=item.get('source','');within(root,source)
  if not source.startswith('10-code/'):raise ValueError('Component source must be inside 10-code')
  if not isinstance(item.get('commands',{}),dict):raise ValueError('Commands must be a mapping')
  for cmd in item.get('commands',{}).values():
   if not isinstance(cmd,list) or not cmd or any(not isinstance(x,str) or not x or '\x00' in x for x in cmd):raise ValueError('Commands must be nonempty argument arrays')
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate component IDs')
 return data
def git(root,*args):
 p=subprocess.run(['git','-C',str(root)]+list(args),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
 return p.stdout.decode('utf-8','replace').strip()
def command_argv(cmd):
 result=list(cmd)
 if os.name=='nt' and result[0]=='npm':
  npm=shutil.which('npm.cmd');node=shutil.which('node');cli=Path(npm).parent/'node_modules/npm/bin/npm-cli.js' if npm else None
  if node and cli and cli.is_file():return [node,str(cli)]+result[1:]
  if npm:return [npm]+result[1:]
 return result
def add_table_row(path,row):
 lines=path.read_text(encoding='utf-8').splitlines();indices=[i for i,x in enumerate(lines) if x.startswith('|')]
 if not indices:raise ValueError('Register table is missing')
 lines.insert(indices[-1]+1,row);path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
