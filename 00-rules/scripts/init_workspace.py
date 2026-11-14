# -*- coding: utf-8 -*-
"""Initialize only a new/empty target. No business source, Git history or deployment."""
from pathlib import Path
import argparse,re,json,shutil,subprocess,os,hashlib
from workspace_core import ROOT
EXCLUDE={'.git','node_modules','__pycache__','.venv'}
def initialize(template,target,project,slug,dry_run=False,init_git=False):
 template=template.resolve();target=target.resolve()
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',slug):raise ValueError('Slug must use lowercase letters, digits and hyphens')
 if not project.strip():raise ValueError('Project name is required')
 if target==template or template in target.parents:raise ValueError('Choose a destination outside the template')
 if target.exists() and (not target.is_dir() or any(target.iterdir())):raise ValueError('Target is not empty; inspect existing work without overwriting it')
 cfg=json.loads((template/'workspace.yaml').read_text(encoding='utf-8'))
 if cfg.get('project',{}).get('mode')!='template' or cfg.get('components'):raise ValueError('Initialize only from the generic template, never from a business project')
 manifest_path=template/'00-rules/template-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));selected=[]
 for name,digest in manifest['files'].items():
  src=(template/name).resolve()
  if template not in src.parents or src.is_symlink() or not src.is_file():raise ValueError('Unsafe or missing template file')
  if hashlib.sha256(src.read_bytes()).hexdigest()!=digest:raise ValueError('Template file changed; review and rebuild the template manifest before distributing it: '+name)
  selected.append((src,Path(name)))
 selected.append((manifest_path,Path('00-rules/template-manifest.json')))
 if dry_run:return {'dryRun':True,'files':len(selected),'createsComponents':False,'deploys':False,'initializesGit':init_git}
 target.mkdir(parents=True,exist_ok=True)
 if any(target.iterdir()):raise ValueError('Target changed after planning')
 for src,relative in selected:
  dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as stream:stream.write(src.read_bytes())
 cfg=json.loads((target/'workspace.yaml').read_text(encoding='utf-8'));cfg['project']={'name':project,'slug':slug,'mode':'product'};cfg['components']=[];(target/'workspace.yaml').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (target/'README.md').write_text('# '+project+'\n\n本项目从通用工作空间模板初始化。名称来自初始化参数，其他产品事实尚未确认；没有业务组件、需求批准或真实部署。\n\n![工作空间](90-assets/diagrams/overview.png)\n\n- [使用指南](00-rules/guides/quickstart.md)\n- [完整流程](00-rules/guides/workflow.md)\n- [AI协作](AGENTS.md)\n- [来源登记](01-inputs/source-register.md)\n- [产品背景](02-product/product-context.md)\n- [规划](03-planning/README.md)\n- [需求池](04-requirement-pool/requirement-pool.md)\n- [需求工作包](05-requirements/README.md)\n- [版本与部署](06-versions/README.md)\n- [评审验收](07-reviews/README.md)\n- [工程源](10-code/README.md)\n- [共享资产](90-assets/README.md)\n- [历史保管](99-archive/README.md)\n- [生成结果](outputs/README.md)\n\n执行python 00-rules/scripts/validate_workspace.py验证结构；业务背景先登记真实来源再填写。\n',encoding='utf-8')
 if init_git:subprocess.run(['git','init',str(target)],check=True,capture_output=True)
 return {'initialized':True,'files':len(selected),'components':0,'deployments':0,'gitInitialized':init_git}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--target',required=True,type=Path);p.add_argument('--project',required=True);p.add_argument('--slug',required=True);p.add_argument('--dry-run',action='store_true');p.add_argument('--git',action='store_true');a=p.parse_args()
 try:result=initialize(ROOT,a.target,a.project,a.slug,a.dry_run,a.git);print(json.dumps(result,ensure_ascii=True))
 except (ValueError,OSError,subprocess.CalledProcessError) as e:p.exit(1,str(e)+'\n')
