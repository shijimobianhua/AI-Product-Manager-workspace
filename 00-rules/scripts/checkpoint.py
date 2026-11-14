# -*- coding: utf-8 -*-
"""Preserve committed root Git history and verify an independent local clone."""
import argparse,re,json,hashlib,subprocess,datetime
from pathlib import Path
from workspace_core import ROOT,git,add_table_row
p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--reason',required=True);a=p.parse_args()
if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,79}',a.id):p.error('Use a unique lowercase checkpoint ID')
if not (ROOT/'.git').exists() or Path(git(ROOT,'rev-parse','--show-toplevel')).resolve()!=ROOT:p.error('The workspace must be the Git root')
if git(ROOT,'status','--porcelain','--untracked-files=all'):p.error('Uncommitted changes: review and commit intended files before checkpointing')
if (ROOT/'.gitmodules').exists():p.error('Define submodule payload coverage first')
for name in git(ROOT,'ls-files','*.gitattributes').splitlines():
 if 'filter=lfs' in (ROOT/name).read_text(encoding='utf-8',errors='replace'):p.error('Git LFS payloads require separate verified preservation')
folder=ROOT/'99-archive/checkpoints'/a.id;probe=ROOT/'outputs/checkpoint-probes'/a.id
if folder.exists() or probe.exists():p.error('Checkpoint ID already exists')
head=git(ROOT,'rev-parse','HEAD');tree=git(ROOT,'rev-parse','HEAD^{tree}');refs=git(ROOT,'for-each-ref','--format=%(refname) %(objectname)')
folder.mkdir(parents=True);probe.parent.mkdir(parents=True,exist_ok=True);bundle=folder/'workspace.bundle';git(ROOT,'bundle','create',str(bundle),'--all','HEAD');git(ROOT,'bundle','verify',str(bundle));subprocess.run(['git','clone','--no-checkout',str(bundle),str(probe)],check=True,capture_output=True)
if git(probe,'rev-parse','HEAD')!=head or git(probe,'rev-parse','HEAD^{tree}')!=tree:raise RuntimeError('Restore probe differs')
if git(ROOT,'rev-parse','HEAD')!=head or git(ROOT,'status','--porcelain','--untracked-files=all') or git(ROOT,'for-each-ref','--format=%(refname) %(objectname)')!=refs:raise RuntimeError('Workspace changed while preserving')
digest=hashlib.sha256(bundle.read_bytes()).hexdigest();receipt={'schemaVersion':1,'id':a.id,'reason':a.reason,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':head,'tree':tree,'payload':{'path':bundle.relative_to(ROOT).as_posix(),'sha256':digest,'bytes':bundle.stat().st_size,'access':'local-only'},'independentCloneVerified':True,'runtimeAcceptance':False,'offDeviceBackup':False,'exclusions':['ignored or uncommitted files','runtime data and credentials','external runtime/LFS/submodule payloads']}
meta=ROOT/'06-versions/checkpoints'/(a.id+'.json');meta.parent.mkdir(parents=True,exist_ok=True);meta.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
add_table_row(ROOT/'06-versions/checkpoint-register.md','| '+a.id+' | `'+head+'` | committed root Git | [receipt](checkpoints/'+meta.name+') | independent clone/tree verified | local-only; no runtime/data guarantee |')
print(json.dumps({'id':a.id,'commit':head,'receipt':meta.relative_to(ROOT).as_posix(),'restoreVerified':True,'note':'Commit the receipt separately; this checkpoint captures the preceding commit'},ensure_ascii=True))
