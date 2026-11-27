from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from threading import RLock
from typing import Protocol
from copy import deepcopy

class RuleViolation(ValueError): pass
class Role(str, Enum):
    REPORTER='REPORTER'; SUPPORT_AGENT='SUPPORT_AGENT'; ADMIN='ADMIN'
class Status(str, Enum):
    OPEN='OPEN'; ASSIGNED='ASSIGNED'; IN_PROGRESS='IN_PROGRESS'; RESOLVED='RESOLVED'; CLOSED='CLOSED'; CANCELLED='CANCELLED'
class Urgency(str, Enum):
    LOW='LOW'; NORMAL='NORMAL'; HIGH='HIGH'
class Priority(str, Enum):
    P1_CRITICAL='P1_CRITICAL'; P2_HIGH='P2_HIGH'; P3_NORMAL='P3_NORMAL'; P4_LOW='P4_LOW'
@dataclass(frozen=True)
class Actor:
    id: str
    role: Role
@dataclass(frozen=True)
class TicketId:
    value: str = field(default_factory=lambda: str(uuid4()))
@dataclass(frozen=True)
class Event:
    ticket_id: TicketId
    version: int
    kind: str
    actor_id: str
    before: str
    after: str
    reason: str
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
class SupportTicket:
    """Aggregate root: all mutations pass through domain behavior."""
    def __init__(self, reporter: Actor, title: str, description: str, category: str, urgency: Urgency):
        if reporter.role != Role.REPORTER or not title.strip() or not description.strip() or not category.strip() or not isinstance(urgency, Urgency):
            raise RuleViolation('Invalid ticket intake')
        self._id=TicketId(); self._reporter=reporter.id; self._title=title; self._description=description; self._category=category; self._urgency=urgency
        self._assignee=None; self._priority=None; self._status=Status.OPEN; self._events=[]
        self._record('CREATED',reporter,'',Status.OPEN.value)
    id=property(lambda s:s._id); reporter_id=property(lambda s:s._reporter); assignee_id=property(lambda s:s._assignee)
    status=property(lambda s:s._status); priority=property(lambda s:s._priority); urgency=property(lambda s:s._urgency)
    events=property(lambda s:tuple(s._events)); version=property(lambda s:len(s._events))
    def _record(self,kind,actor,before,after,reason=''):
        self._events.append(Event(self.id,self.version+1,kind,actor.id,before,after,reason))
    def _transition(self,actor,target):
        old=self.status; self._status=target; self._record('STATUS_CHANGED',actor,old.value,target.value)
    def claim(self,actor):
        if actor.role != Role.SUPPORT_AGENT or self.status != Status.OPEN or self.assignee_id is not None: raise RuleViolation('Claim denied or conflict')
        self._assignee=actor.id; self._status=Status.ASSIGNED; self._record('CLAIMED',actor,'OPEN',actor.id)
    def reassign(self,admin,agent):
        if admin.role != Role.ADMIN or agent.role != Role.SUPPORT_AGENT or self.status not in (Status.ASSIGNED,Status.IN_PROGRESS): raise RuleViolation('Reassignment denied')
        old=self.assignee_id; self._assignee=agent.id; self._record('REASSIGNED',admin,old,agent.id)
    def set_priority(self,actor,priority,reason=''):
        if not isinstance(priority,Priority) or self.status not in (Status.ASSIGNED,Status.IN_PROGRESS) or not (actor.role==Role.ADMIN or (actor.role==Role.SUPPORT_AGENT and actor.id==self.assignee_id)): raise RuleViolation('Priority denied')
        if self.priority is not None and not reason.strip(): raise RuleViolation('Reason required')
        old=self.priority; self._priority=priority; self._record('PRIORITY_CHANGED',actor,old.value if old else '',priority.value,reason)
    def advance(self,actor,target):
        assigned=actor.role==Role.SUPPORT_AGENT and actor.id==self.assignee_id
        owner=actor.role==Role.REPORTER and actor.id==self.reporter_id
        allowed=(self.status==Status.ASSIGNED and target==Status.IN_PROGRESS and assigned and self.priority is not None) or (self.status==Status.IN_PROGRESS and target==Status.RESOLVED and assigned) or (self.status==Status.RESOLVED and target==Status.CLOSED and (owner or actor.role==Role.ADMIN)) or (self.status==Status.OPEN and target==Status.CANCELLED and owner)
        if not allowed: raise RuleViolation('Invalid transition or actor')
        self._transition(actor,target)
class TicketRepository(Protocol):
    def add(self,ticket:SupportTicket): ...
    def get(self,id:TicketId)->SupportTicket: ...
    def save(self,ticket:SupportTicket,expected_version:int): ...
class MemoryTicketRepository:
    """Adapter with optimistic version check under a lock; not distributed persistence."""
    def __init__(self): self._items={}; self._lock=RLock()
    def add(self,ticket):
        with self._lock:
            if ticket.id in self._items: raise RuleViolation('Duplicate ticket')
            self._items[ticket.id]=deepcopy(ticket)
    def get(self,id):
        with self._lock: return deepcopy(self._items[id])
    def save(self,ticket,expected_version):
        with self._lock:
            if self._items[ticket.id].version!=expected_version: raise RuleViolation('Concurrent modification')
            self._items[ticket.id]=deepcopy(ticket)
class ConversationPolicy:
    """Cross-context domain service; uses current ticket state, not cached events."""
    @staticmethod
    def can_write(ticket,actor):
        return ticket.status in (Status.ASSIGNED,Status.IN_PROGRESS) and (actor.role==Role.ADMIN or (actor.role==Role.REPORTER and actor.id==ticket.reporter_id) or (actor.role==Role.SUPPORT_AGENT and actor.id==ticket.assignee_id))
class ClaimTicket:
    def __init__(self,repository:TicketRepository): self.repository=repository
    def execute(self,id,actor):
        ticket=self.repository.get(id); version=ticket.version; ticket.claim(actor); self.repository.save(ticket,version); return ticket
