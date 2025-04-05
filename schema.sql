CREATE TABLE admins (
    user_id INTEGER PRIMARY KEY,
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
    processed_timestamp TEXT
);
CREATE TABLE email_files (
    message_rowid INTEGER,
    file_path TEXT
);

CREATE TABLE tg_users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    registration_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    last_message_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    organization_name TEXT,
    request_timestamp TEXT,
    is_request_declined INTEGER DEFAULT 0,
    manager_name TEXT
);