import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"lib"))
import canonical_ledger as c
class MigrationTests(unittest.TestCase):
 def legacy(self,d,authorized=False):
  d.mkdir();
  docs={"state.json":{"schema_version":1,"change_id":"old","mode":"standard","phase":"SHIP","base_commit":"a"*40},"requirements.json":{"schema_version":1,"requirements":[{"id":"REQ-1","statement":"Preserve behavior","unknown":"kept"}]},"acceptance.json":{"schema_version":1,"criteria":[{"id":"AC-1","requirement_id":"REQ-1","statement":"Test it","evidence":[{"provider":"unit_test","check_id":"x"}]}]},"risk.json":{"risk_level":"standard","control_plane_change":False,"security_privacy_sensitive":False,"migration_or_release_sensitive":False,"high_blast_radius":False,"requires_exec_plan":False},"effects.json":{"external_effects":[],"effect_capabilities":[],"irreversible":False,"authorization_required":False},"authorization.json":{"required":False,"authorized":authorized,"authority":"human" if authorized else "","scope":"legacy only" if authorized else "","evidence_reference":"chat" if authorized else ""}}
  for n,v in docs.items():(d/n).write_text(json.dumps(v))
  (d/"proposal.md").write_text("# Proposal\n\n## Objective\nPreserve old meaning exactly.\n");(d/"scope.txt").write_text("src/**\n");(d/"gate-log.jsonl").write_text(json.dumps({"ts":"2020-01-01T00:00:00Z","event":"START","result":"PASS"})+"\n");(d/"mystery.json").write_text('{"future":true}')
 def test_deterministic_idempotent_and_loss_preserving(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);src=root/"old";self.legacy(src);a=root/"a";b=root/"b";ra=c.migrate_legacy(src,a);rb=c.migrate_legacy(src,b)
   self.assertEqual((a/"intent.json").read_bytes(),(b/"intent.json").read_bytes());self.assertEqual((a/"events.jsonl").read_bytes(),(b/"events.jsonl").read_bytes());self.assertEqual(c.migrate_legacy(src,a)["status"],"UNCHANGED")
   intent=c.load_intent(a);self.assertEqual(intent["requirements"][0]["unknown"],"kept");self.assertEqual(list((a/"grants").glob("*")),[]);self.assertEqual(intent["provenance"]["sources"]["authorization"]["knowledge"],"KNOWN")
 def test_missing_authority_and_evidence_remain_absent(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);src=root/"old";self.legacy(src);(src/"authorization.json").unlink();(src/"acceptance.json").unlink();out=root/"out";c.migrate_legacy(src,out);i=c.load_intent(out)
   self.assertEqual(i["evidence_requirements"],[]);self.assertEqual(i["provenance"]["sources"]["authorization"]["knowledge"],"ABSENT");self.assertFalse(any((out/"grants").iterdir()))
 def test_hostile_json_and_identity_collision_block(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);src=root/"old";self.legacy(src);(src/"risk.json").write_text("{")
   with self.assertRaisesRegex(RuntimeError,"invalid"):c.migrate_legacy(src,root/"out")
if __name__=="__main__":unittest.main()
