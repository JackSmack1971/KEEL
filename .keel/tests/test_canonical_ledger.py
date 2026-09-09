import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"lib"))
import canonical_ledger as c
class CanonicalLedgerTests(unittest.TestCase):
 def intent(self):
  x=c.blank_intent("change","a"*40);x.update(objective="A sufficiently concrete objective",scope=["src/**"],requirements=[{"id":"REQ-1","statement":"Required behavior","source":{"kind":"human"}}],evidence_requirements=[{"id":"ER-1","requirement_id":"REQ-1","statement":"Tests establish behavior","evidence":[{"provider":"unit_test","check_id":"tests"}]}]);return x
 def test_create_chain_projection_and_record_integrity(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td)/"change";c.create(d,self.intent());a=c.append_event(d,"DISCUSS","PASS",timestamp="2020-01-01T00:00:00+00:00");b=c.append_event(d,"PLAN","PASS",timestamp="2020-01-01T00:00:01+00:00")
   self.assertEqual(b["previous_event_digest"],a["event_digest"]);self.assertEqual(c.phase(d),"EXECUTE");self.assertIn("NON-AUTHORITATIVE",(d/"views/summary.md").read_text())
   r=c.record(d,"receipts",{"receipt_id":"r1","subject":{"digest":"x"},"result":"PASS"},"receipt_id");self.assertEqual(r["record_digest"],c.digest({k:v for k,v in r.items() if k not in {"record_digest","generated_by"}}))
 def test_tamper_and_hostile_scope_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td)/"change";c.create(d,self.intent());rows=(d/"events.jsonl").read_text().replace('"result":"PASS"','"result":"FAIL"');(d/"events.jsonl").write_text(rows)
   with self.assertRaisesRegex(RuntimeError,"integrity"):c.read_events(d)
  x=self.intent();x["scope"]=["../escape"]
  self.assertTrue(any("unsafe scope" in e for e in c.validate_intent(x)))
  x=self.intent();x["scope"]=[".github/workflows/ci.yml"]
  self.assertEqual(c.validate_intent(x),[])
  x["scope"]=[".git/config"]
  self.assertTrue(any("unsafe scope" in e for e in c.validate_intent(x)))
 def test_stable_event_identity(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   for td in (a,b):
    d=Path(td)/"change";c.create(d,self.intent());(d/"events.jsonl").unlink();c.append_event(d,"START","PASS",{"base_commit":"a"*40},timestamp="2020-01-01T00:00:00+00:00")
   self.assertEqual((Path(a)/"change/events.jsonl").read_bytes(),(Path(b)/"change/events.jsonl").read_bytes())
if __name__=="__main__":unittest.main()
