CREATE TRIGGER trg_txn_update_balance AFTER INSERT ON transactions
BEGIN
  UPDATE accounts SET balance = balance + CASE NEW.txn_type WHEN 'CREDIT' THEN NEW.amount ELSE -NEW.amount END
  WHERE account_id = NEW.account_id;
END;
CREATE TRIGGER trg_complaint_fraud_flag AFTER INSERT ON complaints
WHEN NEW.txn_id IS NOT NULL AND EXISTS (
  SELECT 1 FROM complaint_categories WHERE category_id = NEW.category_id
  AND name = 'Fraud / Unauthorized Transaction'
)
BEGIN
  INSERT INTO fraud_flags (txn_id, complaint_id, source, reason, severity)
  VALUES (NEW.txn_id, NEW.complaint_id, 'NLP', 'Fraud complaint classification',
    CASE COALESCE(NEW.urgency, 'LOW') WHEN 'HIGH' THEN 'HIGH' WHEN 'MEDIUM' THEN 'MEDIUM' ELSE 'LOW' END);
  UPDATE transactions SET status = 'DISPUTED' WHERE txn_id = NEW.txn_id;
END;
CREATE TRIGGER trg_complaint_status_audit AFTER UPDATE OF status ON complaints
WHEN OLD.status <> NEW.status
BEGIN
  INSERT INTO complaint_actions (complaint_id, action, note)
  VALUES (NEW.complaint_id, 'STATUS_CHANGED', 'Status changed from ' || OLD.status || ' to ' || NEW.status);
  UPDATE complaints SET resolved_at = CASE WHEN NEW.status = 'RESOLVED' THEN datetime('now') ELSE resolved_at END
  WHERE complaint_id = NEW.complaint_id;
END;
