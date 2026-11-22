CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    citation_key TEXT,

    author TEXT,
    editor TEXT,
    organization TEXT,
    school TEXT,
    publisher TEXT,

    publish_year INTEGER,
    publication_date TEXT,
    access_date TEXT,
    howpublished TEXT,


    journal TEXT,
    booktitle TEXT,
    volume TEXT,
    number TEXT,
    issue TEXT,
    chapter TEXT,
    pages TEXT,
    series TEXT,

    doi TEXT,
    isbn TEXT,
    issn TEXT,
    url TEXT,

    keywords TEXT,
    note TEXT,
    extra_fields TEXT,
    hidden INTEGER DEFAULT 0
);
