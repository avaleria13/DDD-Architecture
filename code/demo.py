from domain import (
    Actor, Role, SupportTicket,
    Urgency, Priority, Status
)

# 1. Create the actors
reporter = Actor("reporter-01", Role.REPORTER)
agent = Actor("agent-01", Role.SUPPORT_AGENT)

# 2. Report an IT incident
ticket = SupportTicket(
reporter,
"Wi-Fi connection problem",
"Cannot connect to the university network.",
"Network",
Urgency.HIGH
)

print("=== FIXIT DDD DEMONSTRATION ===")
print(f"\nTicket ID: {ticket.id.value}")
print(f"Reporter urgency: {ticket.urgency.value}")
print(f"Status: {ticket.status.value}")

# 3. Agent claims the ticket
ticket.claim(agent)
print(f"\nTicket claimed by: {ticket.assignee_id}")
print(f"Status: {ticket.status.value}")

# 4. Assign official priority
ticket.set_priority(agent, Priority.P2_HIGH)
print(f"\nOfficial priority: {ticket.priority.value}")

# 5. Start working
ticket.advance(agent, Status.IN_PROGRESS)
print(f"\nStatus: {ticket.status.value}")

# 6. Resolve the incident
ticket.advance(agent, Status.RESOLVED)
print(f"Status: {ticket.status.value}")

# 7. Reporter closes the ticket
ticket.advance(reporter, Status.CLOSED)
print(f"Status: {ticket.status.value}")

# 8. Display the event history
print("\n=== TICKET EVENT HISTORY ===")

for event in ticket.events:
    print(
    f"Version {event.version} | "
    f"{event.kind} | "
    f"Actor: {event.actor_id} | "
    f"{event.before} -> {event.after}"
    )

print(f"\nFinal aggregate version: {ticket.version}")