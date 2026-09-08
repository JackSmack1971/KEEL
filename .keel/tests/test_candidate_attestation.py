from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'.keel/lib'))
from candidate_attestation import CandidateAttestation, SCHEMA, VERSION
D='a'*64

def main():
  value={'change_id':'change','work_identity':{'change_id':'change','base_commit':'b'*40},'candidate_commit':'c'*40,'candidate_tree':'d'*40,'intent_digest':D,'material_digest':D,'content_digest':D,'evidence_plan_digest':D,'evidence_receipts':[{'receipt_id':'tests','receipt_digest':D}],'policy_runtime_profile_digest':D,'changed_paths':['src/a.py'],'schema':SCHEMA,'version':VERSION}
  first=CandidateAttestation.from_dict(value); second=CandidateAttestation.from_dict(json.loads(json.dumps(value,sort_keys=True)))
  assert first==second and first.digest==second.digest and first.as_dict()==value
  for mutation in ({**value,'version':2},{key:val for key,val in value.items() if key!='candidate_tree'},{**value,'intent_digest':'bad'}):
    try: CandidateAttestation.from_dict(mutation)
    except RuntimeError: pass
    else: raise AssertionError('invalid attestation accepted')
  docs='\n'.join((ROOT/p).read_text() for p in ('ARCHITECTURE.md','WORKFLOW.md','docs/control-plane/KEEL.md','docs/control-plane/KERNEL_REDESIGN.md'))
  assert 'CandidateAttestation' in docs and 'Landing Transaction' in docs and 'mutable' in docs
  print('Candidate attestation tests PASS')
if __name__=='__main__': main()
