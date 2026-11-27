REFERENCE_FIELD_SCHEMAS = {
    "article": {
        "required": ["name", "author"],
        "optional": [
            "journal", "publish_year", "publish_month",
            "volume", "number", "pages", "doi", "url", "isbn", "issn", "note"
        ]
    },

    "book": {
        "required": ["name", "author"],
        "optional": [
            "publisher", "publish_year", "chapter",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "booklet": {
        "required": ["name", "author"],
        "optional": [
            "howpublished", "publish_year", "publish_month",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "inbook": {
        "required": ["name", "author"],
        "optional": [
            "booktitle", "publish_year", "publisher", "pages",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "incollection": {
        "required": ["name", "author"],
        "optional": [
            "editor", "booktitle", "publish_year", "publisher", "pages",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "inproceedings": {
        "required": ["name", "author"],
        "optional": [
            "booktitle", "series", "publish_year", "pages", "publisher",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "manual": {
        "required": ["name", "author"],
        "optional": [
            "organization", "publish_year", "doi", "url", "isbn", "issn", "note"
        ]
    },

    "mastersthesis": {
        "required": ["name", "author"],
        "optional": [
            "school", "publish_year", "publish_month",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "misc": {
        "required": ["name", "author"],
        "optional": [
            "howpublished", "publish_year",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "phdthesis": {
        "required": ["name", "author"],
        "optional": [
            "school", "publish_year", "publish_month",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "proceedings": {
        "required": ["name", "author"],
        "optional": [
            "editor", "series", "volume", "publisher", "publish_year",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "techreport": {
        "required": ["name", "author"],
        "optional": [
            "organization", "number", "publish_year", "publish_month",
            "doi", "url", "isbn", "issn", "note"
        ]
    },

    "unpublished": {
        "required": ["name", "author"],
        "optional": [
            "publish_year", "doi", "url", "isbn", "issn", "note"
        ]
    },

    "online": {
        "required": ["name", "author"],
        "optional": [
            "publish_year", "organization", "url",
            "doi", "isbn", "issn", "note"
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
        "publish_month": "Month",
        "howpublished": "HowPublished",

        "journal": "Journal",
        "booktitle": "BookTitle",
        "volume": "Volume",
        "number": "Number",
        "chapter": "Chapter",
        "pages": "Pages",
        "series": "Series",

        "doi": "DOI",
        "isbn": "ISBN",
        "issn": "ISSN",
        "url": "URL",

        "keywords": "Keywords",
        "note": "Note",
        "extra_fields": "Additional Fields",
    }

def bibtex_field_to_table_field(field):
    for column in FIELD_LABELS:
        if field == FIELD_LABELS[column].lower():
            return column