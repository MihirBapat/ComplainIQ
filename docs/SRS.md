# Software Requirements Specification
## Purpose and scope
Fraud-Aware Transaction Complaint Analyzer records banking complaints, classifies their text, and joins NLP results with deterministic transaction-risk rules.
## Users
Customers submit complaints; Agents review complaints and flags; Admins manage customers, accounts, and model information.
## Functional requirements
- FR-1 Staff authenticate with role-based access.
- FR-2 Admins manage customers, accounts, and transactions.
- FR-3 Customers submit a complaint using registered email and account number.
- FR-4 The system stores category, confidence, VADER sentiment, and heuristic urgency.
- FR-5 Fraud complaints linked to transactions create an NLP flag and dispute the transaction.
- FR-6 New transactions run amount-spike, velocity, and location-change rules.
- FR-7 Staff review flags, update complaints, override categories, and add notes.
- FR-8 Dashboard and reports expose operational metrics.
## Non-functional requirements
SQLite foreign keys are enabled; writes use parameterized SQL; Bootstrap provides responsive pages; friendly error pages avoid stack traces.
## Constraints and assumptions
Flask, SQLite raw SQL, scikit-learn, and VADER are required. Urgency is a transparent heuristic, not a predictive model. See `erd.mmd` for the entity model.
