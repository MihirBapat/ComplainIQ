CREATE TABLE account_types (
  type_id INTEGER PRIMARY KEY AUTOINCREMENT,
  type_name TEXT NOT NULL UNIQUE
);
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
  phone TEXT, city TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE accounts (
  account_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
  type_id INTEGER NOT NULL REFERENCES account_types(type_id),
  account_number TEXT NOT NULL UNIQUE,
  balance REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','FROZEN','CLOSED')),
  opened_on TEXT NOT NULL DEFAULT (date('now'))
);
CREATE TABLE transactions (
  txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
  txn_type TEXT NOT NULL CHECK (txn_type IN ('CREDIT','DEBIT')),
  amount REAL NOT NULL CHECK (amount > 0), merchant TEXT, location TEXT,
  txn_time TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED','DISPUTED','REVERSED'))
);
CREATE TABLE complaint_categories (
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE model_versions (
  model_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, accuracy REAL, macro_f1 REAL,
  trained_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE staff (
  staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('ADMIN','AGENT'))
);
CREATE TABLE complaints (
  complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
  account_id INTEGER REFERENCES accounts(account_id),
  txn_id INTEGER REFERENCES transactions(txn_id),
  complaint_text TEXT NOT NULL CHECK (length(complaint_text) >= 20),
  submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','IN_REVIEW','RESOLVED','REJECTED')),
  category_id INTEGER REFERENCES complaint_categories(category_id), confidence REAL,
  sentiment_score REAL,
  sentiment_label TEXT CHECK (sentiment_label IN ('NEGATIVE','NEUTRAL','POSITIVE')),
  urgency TEXT CHECK (urgency IN ('LOW','MEDIUM','HIGH')),
  model_id INTEGER REFERENCES model_versions(model_id), resolved_at TEXT
);
CREATE TABLE fraud_flags (
  flag_id INTEGER PRIMARY KEY AUTOINCREMENT,
  txn_id INTEGER NOT NULL REFERENCES transactions(txn_id) ON DELETE CASCADE,
  complaint_id INTEGER REFERENCES complaints(complaint_id) ON DELETE SET NULL,
  source TEXT NOT NULL CHECK (source IN ('RULE','NLP','MANUAL')),
  reason TEXT NOT NULL, severity TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH')),
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','CONFIRMED','DISMISSED')),
  reviewed_by INTEGER REFERENCES staff(staff_id),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE complaint_actions (
  action_id INTEGER PRIMARY KEY AUTOINCREMENT,
  complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id) ON DELETE CASCADE,
  staff_id INTEGER REFERENCES staff(staff_id), action TEXT NOT NULL, note TEXT,
  acted_at TEXT NOT NULL DEFAULT (datetime('now'))
);
