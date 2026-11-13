from flask import redirect, render_template, request, url_for
from config import app
from db_helper import add_source, get_all_sources, get_source


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

    return render_template("reference.html", reference=reference)
