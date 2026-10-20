# Project Progress

## Phase checklist

- [x] 1. Scaffold — `python run.py` served `/` successfully (HTTP 200, 2026-10-20).
- [x] 2. Database — `python -m pytest tests/test_db.py -v`: 3 passed (2026-10-20).
- [x] 3. Data + ML — processed 15,000 balanced rows and trained TF-IDF + Logistic Regression: accuracy 0.9997, macro-F1 0.9997 (2026-10-20).
- [x] 4. NLP service + fraud rules — `python -m pytest tests/test_nlp.py tests/test_rules.py -v`: 6 passed (2026-10-20).
- [ ] 5. Seed data
- [ ] 6. Auth + CRUD GUI
- [ ] 7. Complaint workflow
- [ ] 8. Dashboard + reports + model page
- [ ] 9. Testing + documentation
- [ ] 10. Polish + final verification

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
