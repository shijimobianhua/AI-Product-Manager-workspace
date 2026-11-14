# -*- coding: utf-8 -*-
"""Execute a reviewed component recipe. No shell concatenation or deployment shortcut."""
import argparse,json,subprocess
from workspace_core import ROOT,read_config,within,command_argv
p=argparse.ArgumentParser();p.add_argument('component',nargs='?');p.add_argument('command',nargs='?');p.add_argument('--list',action='store_true');a=p.parse_args();cfg=read_config(ROOT)
if a.list:print(json.dumps([{'id':x['id'],'type':x.get('type'),'source':x['source'],'commands':list(x.get('commands',{}))} for x in cfg['components']],ensure_ascii=True))
else:
 item=next((x for x in cfg['components'] if x['id']==a.component),None)
 if item is None or a.command not in item.get('commands',{}):p.error('Unknown component/command. Real components must be registered first.')
 if a.command not in ['install','build','test','lint','check','package','export']:p.error('Production deployment needs a separate authorized flow')
 source=within(ROOT,item['source'])
 if not source.is_dir():p.error('Component source does not exist')
 raise SystemExit(subprocess.run(command_argv(item['commands'][a.command]),cwd=str(source)).returncode)
