import re

from flask import redirect, render_template, request, url_for
from config import app
from db_helper import add_source, get_all_sources, get_source


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
    reference_type = (reference.type or "").strip().lower()
    entry_types = {
        "article": "article",
        "book": "book",
        "conference": "inproceedings",
        "conference paper": "inproceedings",
        "journal article": "article",
        "online": "online",
        "web page": "online",
        "webpage": "online",
        "website": "online",
    }
    entry_type = entry_types.get(reference_type, "misc")
    author = reference.author or ""
    author_name = author.split(" and ", 1)[0].strip()
    surname = author_name.split(",", 1)[0] if "," in author_name else author_name.split()[-1] if author_name else ""
    key_parts = (surname, reference.publish_year, reference.name)
    citation_key = "".join(re.sub(r"[^A-Za-z0-9]", "", str(part)) for part in key_parts)
    citation_key = citation_key or "Reference"

    fields = [("title", reference.name)]
    if author:
        fields.append(("author", author))
    if reference.publish_year:
        fields.append(("year", reference.publish_year))
    if reference.url:
        fields.append(("url", reference.url))

    formatted_fields = ",\n".join(
        f"  {field} = {{{_escape_bibtex(value)}}}" for field, value in fields
    )
    return f"@{entry_type}{{{citation_key},\n{formatted_fields}\n}}"


@app.route("/")
def index():
    references = get_all_sources()

    return render_template("index.html", references=references, form_values={})


@app.route("/", methods=["POST"])
def create_reference():
    form_values = request.form
    name = form_values.get("name", "").strip()
    publish_year_value = form_values.get("publish_year", "").strip()
    error = None

    if not name:
        error = "Reference title is required."
    elif publish_year_value:
        try:
            publish_year = int(publish_year_value)
        except ValueError:
            error = "Publish year must be a whole number."
            publish_year = None
    else:
        publish_year = None

    if error:
        return render_template(
            "index.html",
            references=get_all_sources(),
            form_values=form_values,
            error=error,
        ), 400

    add_source(
        name,
        form_values.get("type", "").strip(),
        form_values.get("author", "").strip(),
        publish_year,
        form_values.get("url", "").strip(),
    )
    return redirect(url_for("index"))


@app.route("/ref/<int:source_id>")
def show_reference(source_id):
    reference = get_source(source_id)

    bibtex = _create_bibtex(reference) if reference else None
    return render_template("reference.html", reference=reference, bibtex=bibtex)
