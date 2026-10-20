# Test Report
Environment: Python 3.14.3, Flask 3.1.3, pytest 9.1.1 on Windows.

| Area | Actual result |
|---|---|
| Database constraints, triggers, views | Pass |
| Text cleaning, VADER, inference, urgency | Pass |
| Fraud amount, velocity, location, duplicate checks | Pass |
| Login and customer CRUD | Pass |

`python -m pytest -v`: **10 passed** (2026-10-21).

Model metrics: accuracy 0.9997; macro-F1 0.9997. The supplied export lacks narratives, so metadata-derived text makes this score non-comparable to free-text performance.
