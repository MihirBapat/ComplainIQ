-- top_customers
SELECT cu.full_name, cu.email, COUNT(c.complaint_id) AS complaint_count FROM customers cu JOIN complaints c ON c.customer_id=cu.customer_id GROUP BY cu.customer_id ORDER BY complaint_count DESC LIMIT 10;
-- resolution_time
SELECT cc.name, AVG(julianday(c.resolved_at)-julianday(c.submitted_at)) AS avg_days FROM complaints c JOIN complaint_categories cc ON cc.category_id=c.category_id WHERE c.resolved_at IS NOT NULL GROUP BY cc.category_id;
-- repeat_flags
SELECT a.account_number, COUNT(*) AS flag_count FROM fraud_flags f JOIN transactions t ON t.txn_id=f.txn_id JOIN accounts a ON a.account_id=t.account_id GROUP BY a.account_id HAVING COUNT(*) >= 3;
-- rule_and_nlp
SELECT DISTINCT f1.txn_id FROM fraud_flags f1 JOIN fraud_flags f2 ON f1.txn_id=f2.txn_id WHERE f1.source='RULE' AND f2.source='NLP';
-- no_complaints
SELECT cu.full_name, cu.email FROM customers cu LEFT JOIN complaints c ON c.customer_id=cu.customer_id WHERE c.complaint_id IS NULL;
-- negative_sentiment
SELECT * FROM v_complaint_overview WHERE sentiment_score < (SELECT AVG(sentiment_score) FROM complaints WHERE sentiment_score < 0);
