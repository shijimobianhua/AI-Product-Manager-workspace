# -*- coding: utf-8 -*-
import unittest,tempfile,sys,json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'00-rules/scripts'))
from init_workspace import initialize
from validate_workspace import validate
from workspace_core import read_config
class WorkspaceTests(unittest.TestCase):
 def test_template_is_structurally_valid(self):self.assertEqual(validate(ROOT),[])
 def test_dry_run_writes_nothing(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';self.assertTrue(initialize(ROOT,target,'Sample','sample',True)['dryRun']);self.assertFalse(target.exists())
 def test_nonempty_target_is_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp);f=target/'keep.txt';f.write_text('keep')
   with self.assertRaises(ValueError):initialize(ROOT,target,'Sample','sample')
   self.assertEqual(f.read_text(),'keep');self.assertEqual(len(list(target.iterdir())),1)
 def test_initialized_product_is_empty_and_valid(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';initialize(ROOT,target,'Sample','sample');cfg=read_config(target);self.assertEqual(cfg['project']['mode'],'product');self.assertEqual(cfg['components'],[]);self.assertFalse((target/'.git').exists());self.assertEqual(validate(target),[])
 def test_component_traversal_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';initialize(ROOT,target,'Sample','sample');p=target/'workspace.yaml';cfg=read_config(target);cfg['components']=[{'id':'bad','source':'../../escape','commands':{}}];p.write_text(json.dumps(cfg))
   with self.assertRaises(ValueError):read_config(target)
 def test_missing_link_is_reported(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';initialize(ROOT,target,'Sample','sample');p=target/'02-product/product-context.md';p.write_text('[missing](absent.md)');self.assertTrue(any('Broken link' in x for x in validate(target)))
 def test_dirty_checkpoint_is_refused_without_payload(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';initialize(ROOT,target,'Sample','sample',init_git=True);result=subprocess.run([sys.executable,str(target/'00-rules/scripts/checkpoint.py'),'--id','cp-dirty','--reason','test'],capture_output=True);self.assertNotEqual(result.returncode,0);self.assertFalse((target/'99-archive/checkpoints/cp-dirty').exists())
 def test_clean_checkpoint_can_be_retrieved(self):
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'product';initialize(ROOT,target,'Sample','sample',init_git=True);env=os.environ.copy();env.update({'GIT_AUTHOR_NAME':'Template Tests','GIT_AUTHOR_EMAIL':'tests@localhost','GIT_COMMITTER_NAME':'Template Tests','GIT_COMMITTER_EMAIL':'tests@localhost'})
   subprocess.run(['git','-C',str(target),'add','.'],check=True,capture_output=True);subprocess.run(['git','-C',str(target),'-c','commit.gpgsign=false','commit','-m','test baseline'],env=env,check=True,capture_output=True);result=subprocess.run([sys.executable,str(target/'00-rules/scripts/checkpoint.py'),'--id','cp-clean','--reason','test'],capture_output=True);self.assertEqual(result.returncode,0,result.stderr);receipt=json.loads((target/'06-versions/checkpoints/cp-clean.json').read_text());self.assertTrue(receipt['independentCloneVerified']);self.assertFalse(receipt['runtimeAcceptance'])

 def test_product_cannot_be_used_as_a_template(self):
  with tempfile.TemporaryDirectory() as tmp:
   product=Path(tmp)/'product';initialize(ROOT,product,'Sample','sample')
   with self.assertRaises(ValueError):initialize(product,Path(tmp)/'other','Other','other')
 def test_unlisted_input_is_not_carried_into_new_product(self):
  import shutil
  with tempfile.TemporaryDirectory() as tmp:
   template=Path(tmp)/'template';template.mkdir();manifest=json.loads((ROOT/'00-rules/template-manifest.json').read_text(encoding='utf-8'))
   for name in list(manifest['files'])+['00-rules/template-manifest.json']:
    dest=template/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(str(ROOT/name),str(dest))
   (template/'01-inputs/private-note.txt').write_text('private input')
   target=Path(tmp)/'product';initialize(template,target,'Sample','sample');self.assertFalse((target/'01-inputs/private-note.txt').exists())

if __name__=='__main__':unittest.main()
