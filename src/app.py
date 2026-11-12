from flask import Flask, render_template
from config import app
from db_helper import get_all_sources, get_source


@app.route("/")
def index():
    references = get_all_sources()

    return render_template("index.html", references=references)


@app.route("/ref/<int:source_id>")
def show_reference(source_id):
    reference = get_source(source_id)

    return render_template("reference.html", reference=reference)
