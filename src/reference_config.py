REFERENCE_FIELD_SCHEMAS = {
    "article": {
        "required": ["name", "author"],
        "optional": [
            "journal", "publish_year", "volume",
            "number", "pages"
        ]
    },

    "book": {
        "required": ["name", "author"],
        "optional": ["publisher", "publish_year", "chapter"]
    },

    "booklet": {
        "required": ["name", "author"],
        "optional": [
            "howpublished",
            "publication_date", "publish_year"
        ]
    },

    "inbook": {
        "required": ["name", "author"],
        "optional": [
            "booktitle", "publish_year",
            "publisher", "pages"
        ]
    },

    "incollection": {
        "required": ["name", "author"],
        "optional": [
            "editor", "booktitle", "publish_year",
            "publisher", "pages"
        ]
    },

    "inproceedings": {
        "required": ["name", "author"],
        "optional": [
            "booktitle", "series", "publish_year",
            "pages", "publisher"
        ]
    },

    "manual": {
        "required": ["name", "author"],
        "optional": [
            "organization", "publish_year"
        ]
    },

    "mastersthesis": {
        "required": ["name", "author"],
        "optional": [
            "school", "publish_year", "publication_date"
        ]
    },

    "misc": {
        "required": ["name", "author"],
        "optional": [
            "howpublished",
            "publish_year", "note"
        ]
    },

    "phdthesis": {
        "required": ["name", "author"],
        "optional": [
            "school", "publish_year", "publication_date"
        ]
    },

    "proceedings": {
        "required": ["name", "author"],
        "optional": [
            "editor", "series", "volume",
            "publisher", "publish_year"
        ]
    },

    "techreport": {
        "required": ["name", "author"],
        "optional": [
            "organization", "number",
            "publish_year", "publication_date"
        ]
    },

    "unpublished": {
        "required": ["name", "author"],
        "optional": ["publish_year"]
    },

    "online": {
        "required": ["name", "author"],
        "optional": [
            "publish_year", "organization",
            "url", "access_date"
        ]
    }
}

ENTRY_TYPE_ALIASES = {
    "Article": "article",
    "Journal article": "article",
    "Book": "book",
    "Booklet": "booklet",
    "Conference": "inproceedings",
    "Conference paper": "inproceedings",
    "Conference proceeding": "proceedings",
    "Technical manual": "manual",
    "Master's thesis": "mastersthesis",
    "PHD's thesis": "phdthesis",
    "Technical report": "techreport",
    "Unpublished": "unpublished",
    "Online source": "online",
    "Web page": "online",
    "Webpage": "online",
    "Website": "online",
}

FIELD_LABELS = {
        "name": "Title",
        "type": "Reference Type",
        "citation_key": "Citation Key",

        "author": "Author",
        "editor": "Editor",
        "organization": "Organization",
        "school": "School",
        "publisher": "Publisher",

        "publish_year": "Year",
        "publication_date": "Date",
        "access_date": "URLDate",
        "howpublished": "HowPublished",

        "journal": "Journal",
        "booktitle": "BookTitle",
        "volume": "Volume",
        "number": "Number",
        "issue": "Issue",
        "chapter": "Chapter",
        "pages": "Pages",
        "series": "Series",

        "doi": "DOI",
        "isbn": "ISBN",
        "issn": "ISSN",
        "url": "URL",

        "keywords": "Keywords",
        "note": "Notes",
        "extra_fields": "Additional Fields",
    }