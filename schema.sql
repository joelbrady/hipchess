create table rooms (
    room INTEGER PRIMARY KEY,
    oauthid INTEGER NOT NULL,
    oauthsecret INTEGER NOT NULL
);

create table games (
    room INTEGER PRIMARY KEY,
    board BLOB,
    turn BLOB,
    last_move BLOB
);
