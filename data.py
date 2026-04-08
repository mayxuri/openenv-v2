"""
Synthetic customer support ticket dataset.
Each ticket includes the ground-truth answer used by the grader.
"""

TASK1_TICKETS = [
    {
        "ticket_id": "T001",
        "subject": "Can't login to my account",
        "body": (
            "I've been trying to login for the past hour but keep getting 'Invalid credentials'. "
            "I'm sure my password is correct because I just changed it yesterday. "
            "Please help me regain access to my account as soon as possible!"
        ),
        "customer_name": "Alice Johnson",
        "account_type": "pro",
        "created_at": "2024-01-15T10:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Internal note: the user passed password reset and is blocked at account authentication.",
            "Support history: there is no active billing dispute on this account.",
        ],
        "answer": {"category": "account"},
    },
    {
        "ticket_id": "T002",
        "subject": "Charged twice for my subscription",
        "body": (
            "I noticed two charges of $49.99 on my credit card statement dated January 10th. "
            "I only have one subscription under this account. "
            "Please refund the duplicate charge immediately."
        ),
        "customer_name": "Bob Martinez",
        "account_type": "pro",
        "created_at": "2024-01-15T11:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Billing ledger note: two successful card captures posted for the same invoice.",
            "Ops note: no sign of account-access or platform reliability issues.",
        ],
        "answer": {"category": "billing"},
    },
    {
        "ticket_id": "T003",
        "subject": "API returning 500 Internal Server Error",
        "body": (
            "Since this morning, all our API calls to /api/v2/users are returning "
            "500 Internal Server Error. This is breaking our production application. "
            "Error: InternalServerError: null pointer exception at line 342. "
            "Please investigate urgently."
        ),
        "customer_name": "Carol Chen",
        "account_type": "enterprise",
        "created_at": "2024-01-15T09:15:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Status page note: a backend service regression is under investigation by platform engineering.",
            "Support triage note: customer billing and user permissions are healthy.",
        ],
        "answer": {"category": "technical"},
    },
    {
        "ticket_id": "T004",
        "subject": "How do I export my project data?",
        "body": (
            "I want to export all my project data to CSV format for analysis. "
            "I've looked through the settings and help docs but can't find the export option. "
            "Could you guide me on how to do this? Thanks!"
        ),
        "customer_name": "David Kim",
        "account_type": "free",
        "created_at": "2024-01-15T14:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Knowledge base note: export is a product-usage question, not an incident.",
            "Customer success note: there is no account lock or invoice issue tied to this request.",
        ],
        "answer": {"category": "general"},
    },
    {
        "ticket_id": "T005",
        "subject": "Invoice not received after plan upgrade",
        "body": (
            "I upgraded my plan from Pro to Enterprise last week but haven't received "
            "the invoice yet. I need it for my company's expense report by end of month. "
            "My account email is eva@techcorp.com."
        ),
        "customer_name": "Eva Wilson",
        "account_type": "enterprise",
        "created_at": "2024-01-15T16:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Finance note: the upgrade charge succeeded but the PDF invoice failed to send.",
            "Customer profile note: login and workspace access are unaffected.",
        ],
        "answer": {"category": "billing"},
    },
    {
        "ticket_id": "T006",
        "subject": "Two-factor authentication code always expired",
        "body": (
            "The 2FA code I receive via SMS is always expired by the time I enter it. "
            "I've checked and my phone's time is synced correctly. "
            "This has effectively locked me out of my account for two days."
        ),
        "customer_name": "Frank Brown",
        "account_type": "pro",
        "created_at": "2024-01-15T13:45:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Identity note: recent MFA failures are isolated to SMS verification, not payments or product bugs.",
            "Security note: this ticket should route with account-access ownership.",
        ],
        "answer": {"category": "account"},
    },
    {
        "ticket_id": "T007",
        "subject": "Dashboard loading extremely slowly",
        "body": (
            "The dashboard has been extremely slow to load for the past 3 days. "
            "It takes over 30 seconds to display the main page. "
            "My internet is fine - other websites load normally. Please investigate."
        ),
        "customer_name": "Grace Lee",
        "account_type": "pro",
        "created_at": "2024-01-15T10:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Performance note: other customers reported elevated dashboard latency during the same window.",
            "Support note: no account-plan or invoicing change explains this behavior.",
        ],
        "answer": {"category": "technical"},
    },
    {
        "ticket_id": "T008",
        "subject": "Difference between Pro and Enterprise plans?",
        "body": (
            "I'm currently on the Pro plan with a team of 50 people. "
            "I'm wondering whether upgrading to Enterprise would be beneficial. "
            "Can you explain the main differences and whether it's worth upgrading for our use case?"
        ),
        "customer_name": "Henry Zhang",
        "account_type": "pro",
        "created_at": "2024-01-15T11:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Sales assist note: this is a product guidance request, not a break-fix issue.",
            "Billing note: the customer is asking for plan advice rather than disputing a charge.",
        ],
        "answer": {"category": "general"},
    },
    {
        "ticket_id": "T009",
        "subject": "Need VAT number added to future invoices",
        "body": (
            "Our finance team needs our company VAT number included on future invoices. "
            "I couldn't find a place to edit it in the billing portal. "
            "Can you update this or tell me where to do it?"
        ),
        "customer_name": "Nina Patel",
        "account_type": "enterprise",
        "created_at": "2024-01-16T09:10:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Finance operations note: the request concerns invoice metadata and tax records.",
            "Support note: the customer's product access is healthy.",
        ],
        "answer": {"category": "billing"},
    },
    {
        "ticket_id": "T010",
        "subject": "New teammate cannot accept workspace invite",
        "body": (
            "We invited a new teammate to our workspace, but the invite link says it has expired "
            "even though it was sent a few minutes ago. "
            "Could you help us get this person added today?"
        ),
        "customer_name": "Owen Brooks",
        "account_type": "pro",
        "created_at": "2024-01-16T12:40:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Admin console note: the workspace invitation record exists but the token was invalidated early.",
            "Routing note: this belongs with account and identity support, not billing.",
        ],
        "answer": {"category": "account"},
    },
]

TASK2_TICKETS = [
    {
        "ticket_id": "T101",
        "subject": "URGENT: Production system completely down",
        "body": (
            "Our entire production environment is down. ALL API calls return 500 errors. "
            "10,000 active users are affected and we are losing approximately $50k per hour. "
            "This started 15 minutes ago with no recent deployments on our end. "
            "CRITICAL EMERGENCY - please respond immediately."
        ),
        "customer_name": "Bob Smith",
        "account_type": "enterprise",
        "created_at": "2024-01-15T14:00:00Z",
        "previous_tickets": [
            {"ticket_id": "T099", "subject": "API latency spike", "resolved": True}
        ],
        "clarifications": [
            "On-call note: multiple enterprise tenants are impacted and incident command is active.",
            "Routing guidance: this should bypass customer success and go directly to platform responders.",
        ],
        "answer": {
            "category": "technical",
            "priority": "critical",
            "team": "technical_team",
        },
    },
    {
        "ticket_id": "T102",
        "subject": "Is dark mode available on mobile?",
        "body": (
            "Hi! I was just wondering whether the dark mode feature is available on the mobile app. "
            "I use it frequently and would love to have dark mode to reduce eye strain. Thanks!"
        ),
        "customer_name": "Sarah Lee",
        "account_type": "free",
        "created_at": "2024-01-15T10:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Knowledge note: the customer is asking for product guidance, not reporting a defect.",
            "Triage note: standard customer success handling is appropriate.",
        ],
        "answer": {
            "category": "general",
            "priority": "low",
            "team": "customer_success",
        },
    },
    {
        "ticket_id": "T103",
        "subject": "Refund request - charged after cancellation",
        "body": (
            "I cancelled my Pro subscription 3 days ago but was still charged $99 for the next month. "
            "I have cancellation confirmation #CANCEL-2024-789. "
            "Please process a full refund to my original payment method."
        ),
        "customer_name": "Michael Johnson",
        "account_type": "free",
        "created_at": "2024-01-15T09:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Billing note: cancellation confirmation exists and post-cancel billing needs investigation.",
            "Risk note: the customer is upset, but service is not production-down.",
        ],
        "answer": {
            "category": "billing",
            "priority": "high",
            "team": "billing_team",
        },
    },
    {
        "ticket_id": "T104",
        "subject": "Cannot change account email address",
        "body": (
            "I'm trying to update my account email from old@company.com to new@company.com "
            "but keep getting 'Email already in use' error even though that email has no account. "
            "This is blocking a staff transition for our 200-person organisation."
        ),
        "customer_name": "Emma Davis",
        "account_type": "enterprise",
        "created_at": "2024-01-15T11:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Identity note: the failure is isolated to account ownership metadata.",
            "Priority note: this is business-impacting but not a platform-wide outage.",
        ],
        "answer": {
            "category": "account",
            "priority": "medium",
            "team": "account_team",
        },
    },
    {
        "ticket_id": "T105",
        "subject": "Webhooks not firing for payment events",
        "body": (
            "Our payment webhook endpoint has not received any events for the past 6 hours. "
            "We rely on this for real-time payment processing in production. "
            "Our server logs show zero incoming requests from your service. "
            "Webhook URL: https://api.ourcompany.com/webhooks/payment"
        ),
        "customer_name": "James Wilson",
        "account_type": "enterprise",
        "created_at": "2024-01-15T08:00:00Z",
        "previous_tickets": [
            {"ticket_id": "T098", "subject": "Webhook setup help", "resolved": True}
        ],
        "clarifications": [
            "Engineering note: event delivery appears stalled for several tenants using the same region.",
            "Priority note: this is urgent revenue-path degradation, but core APIs remain online.",
        ],
        "answer": {
            "category": "technical",
            "priority": "high",
            "team": "technical_team",
        },
    },
    {
        "ticket_id": "T106",
        "subject": "Invoice shows wrong amount",
        "body": (
            "The invoice for January shows $199/month but I'm on the $99/month Pro plan. "
            "This appears to be a billing error. Please correct the invoice and issue a revised one."
        ),
        "customer_name": "Lisa Thompson",
        "account_type": "pro",
        "created_at": "2024-01-15T15:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Finance note: the account's contracted rate is indeed $99 per month.",
            "Priority note: this requires prompt billing follow-up but is not a service outage.",
        ],
        "answer": {
            "category": "billing",
            "priority": "medium",
            "team": "billing_team",
        },
    },
    {
        "ticket_id": "T107",
        "subject": "SSO login loop for all employees",
        "body": (
            "Since this morning, every employee who tries to sign in with Okta gets redirected back to the login page. "
            "No one can access the workspace through SSO right now. "
            "Password login is disabled due to our security policy."
        ),
        "customer_name": "Priya Nair",
        "account_type": "enterprise",
        "created_at": "2024-01-16T07:20:00Z",
        "previous_tickets": [
            {"ticket_id": "T088", "subject": "SSO setup review", "resolved": True}
        ],
        "clarifications": [
            "Identity operations note: SAML assertions are failing validation for this tenant.",
            "Impact note: full workforce access is blocked, but the wider platform is still up.",
        ],
        "answer": {
            "category": "account",
            "priority": "high",
            "team": "account_team",
        },
    },
    {
        "ticket_id": "T108",
        "subject": "Feature request: scheduled PDF exports",
        "body": (
            "Our team would love a way to schedule PDF exports every Friday for management reporting. "
            "This is not urgent, but we'd like to know whether it exists or is on the roadmap."
        ),
        "customer_name": "Rachel Green",
        "account_type": "pro",
        "created_at": "2024-01-16T10:25:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Product note: this is a roadmap and usage conversation rather than an incident.",
            "Routing note: customer success should own follow-up.",
        ],
        "answer": {
            "category": "general",
            "priority": "low",
            "team": "customer_success",
        },
    },
]

TASK3_TICKETS = [
    {
        "ticket_id": "T201",
        "subject": "Refund request - duplicate charge",
        "body": (
            "I was charged $99 twice on January 10th for my Pro subscription. "
            "I only have one account. Please refund the duplicate charge. "
            "My account email is carol@startup.com."
        ),
        "customer_name": "Carol Davis",
        "account_type": "pro",
        "created_at": "2024-01-15T09:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Billing note: the duplicate charge is visible and pending manual review.",
            "SLA note: refunds usually settle within five business days after approval.",
        ],
        "answer": {
            "must_include_words": ["carol", "refund", "apologize"],
            "issue_keywords": ["duplicate", "charge"],
            "resolution_phrases": ["process", "business days", "team", "investigate", "confirm"],
            "action_phrases": ["review", "refund", "confirm", "follow up"],
            "empathy_phrases": ["sorry", "apologize", "understand"],
            "forbidden_phrases": ["guaranteed immediately", "instantly refunded", "we already fixed everything"],
            "min_words": 60,
            "max_words": 500,
        },
    },
    {
        "ticket_id": "T202",
        "subject": "URGENT: Cannot access data - production demo in 2 hours",
        "body": (
            "We cannot access any of our data. All API calls return 403 Forbidden since this morning. "
            "We have a demo with a major client in 2 hours. Our API key is still active. "
            "Please HELP URGENTLY."
        ),
        "customer_name": "David Park",
        "account_type": "enterprise",
        "created_at": "2024-01-15T08:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "On-call note: platform responders have been paged and this case is marked urgent.",
            "Customer context: the team needs a status update plus the next troubleshooting step quickly.",
        ],
        "answer": {
            "must_include_words": ["david", "apologize"],
            "issue_keywords": ["403", "access"],
            "resolution_phrases": ["escalate", "investigate", "team", "immediately", "priority"],
            "action_phrases": ["escalated", "investigate", "update", "priority"],
            "empathy_phrases": ["sorry", "apologize", "understand"],
            "forbidden_phrases": ["issue is resolved", "guaranteed fix in 10 minutes"],
            "min_words": 80,
            "max_words": 500,
        },
    },
    {
        "ticket_id": "T203",
        "subject": "How to set up SSO with Okta for our team?",
        "body": (
            "We are an enterprise customer and want to set up Single Sign-On (SSO) for our 200-person team. "
            "We use Okta as our identity provider. "
            "Can you walk us through the setup process?"
        ),
        "customer_name": "Emma Rodriguez",
        "account_type": "enterprise",
        "created_at": "2024-01-15T14:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Enablement note: the customer needs a step-by-step setup path and where to find docs.",
            "Support note: this is onboarding guidance, not an outage.",
        ],
        "answer": {
            "must_include_words": ["emma", "sso"],
            "issue_keywords": ["okta", "sso", "single sign"],
            "resolution_phrases": ["steps", "settings", "configuration", "guide", "documentation", "support"],
            "action_phrases": ["navigate", "configure", "review", "contact support"],
            "empathy_phrases": ["happy to help", "glad to help", "happy to walk"],
            "forbidden_phrases": ["done for you already", "enabled on your behalf"],
            "min_words": 80,
            "max_words": 600,
        },
    },
    {
        "ticket_id": "T204",
        "subject": "Password reset email never arrives",
        "body": (
            "I requested a password reset three times today but never received the email. "
            "I've checked spam/junk folders. My email is frank@example.com. "
            "I'm completely locked out of my account."
        ),
        "customer_name": "Frank Adams",
        "account_type": "free",
        "created_at": "2024-01-15T12:00:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Support note: email delivery is delayed for a subset of reset emails.",
            "Recovery note: manual account recovery is available if email delivery fails.",
        ],
        "answer": {
            "must_include_words": ["frank", "apologize"],
            "issue_keywords": ["password", "email", "reset"],
            "resolution_phrases": ["team", "investigate", "manually", "send", "alternative"],
            "action_phrases": ["investigate", "send", "recover", "update"],
            "empathy_phrases": ["sorry", "apologize", "understand"],
            "forbidden_phrases": ["password has been reset already", "email was definitely delivered"],
            "min_words": 60,
            "max_words": 400,
        },
    },
    {
        "ticket_id": "T205",
        "subject": "Need export for audit by Friday",
        "body": (
            "Our finance auditors need a full activity export by Friday, but I cannot find the right report. "
            "Could you point me to the correct export flow and let me know if support can help if fields are missing?"
        ),
        "customer_name": "Melissa Grant",
        "account_type": "enterprise",
        "created_at": "2024-01-16T11:30:00Z",
        "previous_tickets": [],
        "clarifications": [
            "Enablement note: the customer needs guidance plus an escalation path if the export lacks fields.",
            "Timing note: the request is deadline-driven but not an incident.",
        ],
        "answer": {
            "must_include_words": ["melissa", "export"],
            "issue_keywords": ["audit", "report", "export"],
            "resolution_phrases": ["steps", "support", "fields", "review", "follow up"],
            "action_phrases": ["navigate", "review", "contact support", "follow up"],
            "empathy_phrases": ["happy to help", "understand", "appreciate"],
            "forbidden_phrases": ["audit completed", "all data is already attached"],
            "min_words": 80,
            "max_words": 450,
        },
    },
]


def get_ticket_for_task(task_name: str, seed: int = 42) -> dict:
    """Return a single deterministic ticket for a task based on seed."""
    if task_name == "classify":
        pool = TASK1_TICKETS
    elif task_name == "route":
        pool = TASK2_TICKETS
    elif task_name == "respond":
        pool = TASK3_TICKETS
    else:
        raise ValueError(f"Unknown task: {task_name}. Choose: classify | route | respond")
    return pool[seed % len(pool)]
