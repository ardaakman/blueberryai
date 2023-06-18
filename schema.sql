DROP TABLE IF EXISTS call_log;
CREATE TABLE call_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    recipient TEXT,
    phone_number TEXT,
    context TEXT,
    personal_info TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS chat;
CREATE TABLE chat (
    id INTEGER PRIMARY KEY,
    call_id INTEGER,
    sender INTEGER,
    message TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
