CREATE TABLE sources(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    author TEXT,
    publish_year INTEGER
);