CREATE TABLE admins (
    tg_user_id INTEGER PRIMARY KEY,
    fsm_state TEXT,
    select_id INTEGER
);

CREATE TABLE email_messages (
    rowid INTEGER PRIMARY KEY,
    account TEXT NOT NULL,
    from_account TEXT NOT NULL,
    message_uid INTEGER NOT NULL,
    message_subject TEXT NOT NULL,
    message_date TEXT NOT NULL,
    record_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    is_processed INTEGER DEFAULT 0, 
    processed_timestamp TEXT,
    success INTEGER,
    error TEXT
);
CREATE TABLE email_files (
    message_rowid INTEGER,
    filepath TEXT
);

CREATE TABLE managers (
    id INTEGER PRIMARY KEY,
    manager_name TEXT,
    tg_user_id INTEGER,
    tg_username TEXT
);
CREATE TABLE users (
    tg_user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    record_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)