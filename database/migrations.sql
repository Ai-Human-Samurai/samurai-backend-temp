PRAGMA foreign_keys=off;

CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language TEXT DEFAULT 'ru',
    style TEXT DEFAULT 'friendly',  
    is_pro BOOLEAN DEFAULT 0,
    pro_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users_new (id, language, style, is_pro, pro_until, created_at)
SELECT id, language, style, is_pro, pro_until, created_at FROM users;

DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

CREATE TABLE reminders_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    time DATETIME,
    is_seen BOOLEAN DEFAULT 0,
    is_played BOOLEAN DEFAULT 0,
    is_completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

INSERT INTO reminders_new (id, user_id, text, time, is_seen, is_played, is_completed, created_at)
SELECT id, user_id, text, time, is_seen, is_played, is_completed, created_at FROM reminders;

DROP TABLE reminders;
ALTER TABLE reminders_new RENAME TO reminders;

CREATE TABLE subscriptions_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    is_active BOOLEAN DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ends_at DATETIME,
    trial_used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

INSERT INTO subscriptions_new (id, user_id, is_active, started_at, ends_at, trial_used)
SELECT id, user_id, is_active, started_at, ends_at, trial_used FROM subscriptions;

DROP TABLE subscriptions;
ALTER TABLE subscriptions_new RENAME TO subscriptions;

PRAGMA foreign_keys=on;
