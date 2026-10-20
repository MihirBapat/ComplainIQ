CREATE INDEX idx_transactions_account_time ON transactions(account_id, txn_time);
CREATE INDEX idx_complaints_customer ON complaints(customer_id);
CREATE INDEX idx_complaints_status_urgency ON complaints(status, urgency);
CREATE INDEX idx_complaints_category ON complaints(category_id);
CREATE INDEX idx_fraud_flags_status ON fraud_flags(status);
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
