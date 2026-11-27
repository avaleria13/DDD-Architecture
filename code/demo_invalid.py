from domain import *

reporter = Actor("reporter-01", Role.REPORTER)
agent = Actor("agent-01", Role.SUPPORT_AGENT)

ticket = SupportTicket(
reporter,
"Wi-Fi problem",
"Cannot connect to the network.",
"Network",
Urgency.HIGH
)

ticket.claim(agent)

# Attempt to start working WITHOUT assigning priority
try:
    ticket.advance(agent, Status.IN_PROGRESS)
except RuleViolation as error:
    print(f"Operation rejected: {error}")

print(f"Current status: {ticket.status.value}")