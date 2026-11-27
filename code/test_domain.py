import unittest
from concurrent.futures import ThreadPoolExecutor
from domain import *
class DomainTests(unittest.TestCase):
    def setUp(self):
        self.r=Actor('r',Role.REPORTER); self.a=Actor('a',Role.SUPPORT_AGENT); self.b=Actor('b',Role.SUPPORT_AGENT); self.admin=Actor('admin',Role.ADMIN)
        self.t=SupportTicket(self.r,'Wi-Fi','Cannot connect','network',Urgency.HIGH)
    def test_lifecycle(self):
        self.t.claim(self.a); self.t.set_priority(self.a,Priority.P2_HIGH); self.t.advance(self.a,Status.IN_PROGRESS); self.t.advance(self.a,Status.RESOLVED); self.t.advance(self.r,Status.CLOSED); self.assertEqual(self.t.status,Status.CLOSED); self.assertEqual(self.t.version,6)
    def test_priority_required(self):
        self.t.claim(self.a)
        with self.assertRaises(RuleViolation): self.t.advance(self.a,Status.IN_PROGRESS)
    def test_reporter_cannot_prioritize(self):
        self.t.claim(self.a)
        with self.assertRaises(RuleViolation): self.t.set_priority(self.r,Priority.P1_CRITICAL)
    def test_priority_reason(self):
        self.t.claim(self.a); self.t.set_priority(self.a,Priority.P2_HIGH)
        with self.assertRaises(RuleViolation): self.t.set_priority(self.a,Priority.P1_CRITICAL)
    def test_reassignment(self):
        self.t.claim(self.a); self.assertTrue(ConversationPolicy.can_write(self.t,self.a)); self.t.reassign(self.admin,self.b); self.assertFalse(ConversationPolicy.can_write(self.t,self.a)); self.assertTrue(ConversationPolicy.can_write(self.t,self.b))
    def test_cancel(self):
        self.t.advance(self.r,Status.CANCELLED); self.assertFalse(ConversationPolicy.can_write(self.t,self.r))
    def test_concurrent_claim(self):
        repo=MemoryTicketRepository(); repo.add(self.t)
        def claim(a):
            try: ClaimTicket(repo).execute(self.t.id,a); return True
            except RuleViolation: return False
        with ThreadPoolExecutor(2) as pool: results=list(pool.map(claim,[self.a,self.b]))
        self.assertEqual(sum(results),1)
    def test_stale_write(self):
        repo=MemoryTicketRepository(); repo.add(self.t); x=repo.get(self.t.id); y=repo.get(self.t.id); x.claim(self.a); y.claim(self.b); repo.save(x,1)
        with self.assertRaises(RuleViolation): repo.save(y,1)
    def test_immutable_id(self):
        with self.assertRaises(AttributeError): self.t.id.value='other'
    def test_outsider(self):
        self.t.claim(self.a); self.assertFalse(ConversationPolicy.can_write(self.t,self.b))
if __name__=='__main__': unittest.main()
