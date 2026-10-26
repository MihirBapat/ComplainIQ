# Project Progress

## Phase checklist

- [x] 1. Scaffold — `python run.py` served `/` successfully (HTTP 200, 2026-10-20).
- [x] 2. Database — `python -m pytest tests/test_db.py -v`: 3 passed (2026-10-20).
- [x] 3. Data + ML — processed 15,000 balanced rows and trained TF-IDF + Logistic Regression: accuracy 0.9997, macro-F1 0.9997 (2026-10-20).
- [x] 4. NLP service + fraud rules — `python -m pytest tests/test_nlp.py tests/test_rules.py -v`: 6 passed (2026-10-20).
- [x] 5. Seed data — `python scripts/seed_db.py --reset`: 200 customers, 300 accounts, 5,003 transactions, 150 complaints; overview view returned 150 rows (2026-10-20).
- [x] 6. Auth + CRUD GUI — account create/edit/delete and transaction filters verified (2026-10-26).
- [x] 7. Complaint workflow — verified fraud complaint classification, HIGH urgency and trigger-created NLP flag (2026-10-26).
- [x] 8. Dashboard + reports + model page — dark operations dashboard and route walkthrough passed (2026-10-26).
- [x] 9. Testing + documentation — test report and design documents added.
- [x] 10. Polish + final verification — `python -m pytest -v`: 10 passed; seeded route walkthrough and complaint workflow passed (2026-10-26).

## Weekly plan

| Week | Planned | Done | Owner | Blockers |
|---|---|---|---|---|
| 1 | SRS draft, ER diagram, schema, normalization | Phases 1–2 scaffold and database complete | Codex | |
| 2 | DB, seed, dataset prep, baseline model | Database and metadata-based model complete | Codex | Missing narrative field documented as deviation |
| 3 | CRUD GUI, NLP service, fraud rules | | Codex | |
| 4 | Complaint workflow, dashboard, reports | | Codex | |
| 5 | Testing, report, demo rehearsal | | Codex | |

## Deviations

| Date | Deviation | Reason / impact |
|---|---|---|
| 2026-10-20 | The supplied 5.6 GB CFPB CSV has no narrative column. `prepare_data.py` uses its real `Product`, `Issue`, and `Sub-issue` fields as the classifier text. | The plan's required narrative filter is impossible with this export. This is explicitly labelled in script output and documentation; model results must be interpreted as metadata-based, not free-text narrative performance. |
| 2026-10-21 | `erd.png` was not exported. | Mermaid source is delivered; the optional CLI was not available in this environment. |
