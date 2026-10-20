CREATE VIEW v_complaint_overview AS
SELECT c.*, cu.full_name AS customer_name, cc.name AS category_name, a.account_number, t.amount AS txn_amount
FROM complaints c JOIN customers cu ON cu.customer_id=c.customer_id
LEFT JOIN complaint_categories cc ON cc.category_id=c.category_id
LEFT JOIN accounts a ON a.account_id=c.account_id LEFT JOIN transactions t ON t.txn_id=c.txn_id;
CREATE VIEW v_fraud_dashboard AS
SELECT f.*, t.amount, t.merchant, t.location, t.txn_time, cu.full_name AS customer_name,
  c.complaint_text FROM fraud_flags f JOIN transactions t ON t.txn_id=f.txn_id
JOIN accounts a ON a.account_id=t.account_id JOIN customers cu ON cu.customer_id=a.customer_id
LEFT JOIN complaints c ON c.complaint_id=f.complaint_id;
CREATE VIEW v_category_stats AS
SELECT cc.name AS category_name, COUNT(c.complaint_id) AS complaint_count,
 AVG(c.sentiment_score) AS avg_sentiment,
 COALESCE(100.0 * SUM(CASE WHEN c.urgency='HIGH' THEN 1 ELSE 0 END) / NULLIF(COUNT(c.complaint_id),0),0) AS high_urgency_percent
FROM complaint_categories cc LEFT JOIN complaints c ON c.category_id=cc.category_id GROUP BY cc.category_id, cc.name;
CREATE VIEW v_monthly_complaints AS
SELECT substr(c.submitted_at,1,7) AS month, cc.name AS category_name, COUNT(*) AS complaint_count
FROM complaints c LEFT JOIN complaint_categories cc ON cc.category_id=c.category_id
GROUP BY substr(c.submitted_at,1,7), cc.name;
