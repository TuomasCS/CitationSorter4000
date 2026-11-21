import re
from urllib.parse import urlsplit

from flask import redirect, render_template, request, url_for, flash
from src.config import app
from src.db_helper import add_source, get_all_sources, get_source
from src.reference_config import (
    REFERENCE_FIELD_SCHEMAS,
    ENTRY_TYPE_ALIASES,
    FIELD_LABELS
)

def _escape_bibtex(value): #converts character latex treats differently into safer options
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return re.sub(r"[\\&%$#_{}~^]", lambda match: replacements[match.group()], str(value))


def _create_bibtex(reference): # converts the information into bibtex
    reference_type = (reference.type or "").strip()

    entry_type = ENTRY_TYPE_ALIASES.get(reference_type, "misc")
    author = reference.author or ""
    author_name = author.split(" and ", 1)[0].strip()
    surname = author_name.split(",", 1)[0] if "," in author_name else author_name.split()[-1] if author_name else ""
    key_parts = (surname, reference.publish_year, reference.name)
    citation_key = "".join(re.sub(r"[^A-Za-z0-9]", "", str(part)) for part in key_parts)
    citation_key = citation_key or "Reference"

    columns = REFERENCE_FIELD_SCHEMAS[entry_type]["required"] + REFERENCE_FIELD_SCHEMAS[entry_type]["optional"]
    fields = []

    for col in columns:
        if reference[col]:
            fields.append((field_label(col).lower(), reference[col]))

    formatted_fields = ",\n".join(
        f"  {field} = {{{_escape_bibtex(value)}}}" for field, value in fields
    )
    return f"@{entry_type}{{{citation_key},\n{formatted_fields}\n}}"

@app.template_filter("field_label")
def field_label(column):
    labels = FIELD_LABELS

    return labels.get(column, column)

@app.route("/")
def index():
    references = get_all_sources()

    return render_template("index.html", references=references, form_values={})

@app.route("/create", methods=["GET", "POST"])
def add_reference():
    is_post = request.method == "POST"
    form_values = request.form if is_post else {}
    type_values = form_values if is_post else request.args
    type_input = type_values.get("type", "").strip()
    entry = ENTRY_TYPE_ALIASES.get(type_input)
    fields = REFERENCE_FIELD_SCHEMAS.get(entry)
    error = None

    if fields is None:
        if is_post or type_input:
            error = "Select a valid reference type."
    elif is_post:
        values = {
            field: form_values.get(field, "").strip()
            for field in fields["required"] + fields["optional"]
        }
        missing = [
            field_label(field) for field in fields["required"] if not values[field]
        ]
        year = values.get("publish_year", "")
        url = values.get("url", "")

        if missing:
            error = f"Required fields: {', '.join(missing)}."
        elif year and not re.fullmatch(r"[0-9]{1,4}", year):
            error = "Publication year must contain one to four digits."
        elif url:
            try:
                parsed = urlsplit(url)
                valid_url = (
                    parsed.scheme in {"http", "https"}
                    and bool(parsed.hostname)
                    and parsed.port != 0
                    and not any(char.isspace() or ord(char) < 32 for char in url)
                )
            except ValueError:
                valid_url = False
            if not valid_url:
                error = "Enter a valid HTTP or HTTPS URL."

        if error is None:
            flash("Reference has beeen successfully added")
            add_source(form_values)
            return redirect(url_for("index"))

    return render_template(
        "add_reference.html",
        type_input=type_input,
        entry_types=ENTRY_TYPE_ALIASES,
        fields=fields,
        form_values=form_values,
        error=error,
    ), 400 if error else 200


@app.route("/ref/<int:source_id>")
def show_reference(source_id):
    reference = get_source(source_id)
    type = ENTRY_TYPE_ALIASES[reference.type]
    fields = REFERENCE_FIELD_SCHEMAS[type]["required"] + REFERENCE_FIELD_SCHEMAS[type]["optional"]

    bibtex = _create_bibtex(reference) if reference else None
    return render_template("reference.html", reference=reference, bibtex=bibtex, fields=fields+['type'])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
