from __future__ import annotations
import importlib.util, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'.keel/lib'))
import git_proof as proof

def git(root,*args): return subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
def main():
  with tempfile.TemporaryDirectory() as td:
    root=Path(td)/'repo'; root.mkdir(); git(root,'init','-q'); (root/'a.txt').write_text('a\n'); git(root,'add','.'); git(root,'-c','user.name=T','-c','user.email=t@x','commit','-qm','base'); base=git(root,'rev-parse','HEAD')
    assert proof.repository_root((root/'a.txt').parent)==root.resolve(); assert proof.head_commit(root)==base
    identity=proof.repository_identity(root,base); assert identity.baseline_commit==base and identity.root==str(root.resolve()) and identity.git_dir==identity.common_dir
    assert proof.normalize_repo_path(r'dir\\file')=='dir/file'
    for unsafe in ('../x','/x','.git/config',''):
      try: proof.normalize_repo_path(unsafe)
      except ValueError: pass
      else: raise AssertionError(unsafe)
    (root/'a.txt').write_text('changed\n'); (root/'new file').write_text('new\n'); assert proof.changed_paths(root,base)==['a.txt','new file']
    git(root,'add','.'); git(root,'-c','user.name=T','-c','user.email=t@x','commit','-qm','candidate'); candidate=git(root,'rev-parse','HEAD'); assert proof.changed_paths(root,base,candidate)==['a.txt','new file']
    linked=Path(td)/'linked'; git(root,'worktree','add','-q','--detach',str(linked),base); linked_id=proof.repository_identity(linked,base)
    assert linked_id.common_dir==identity.common_dir and linked_id.git_dir!=identity.git_dir and linked_id.worktree==str(linked.resolve())
  print('Git proof tests PASS')
if __name__=='__main__': main()
