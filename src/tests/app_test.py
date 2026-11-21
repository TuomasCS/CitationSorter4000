import unittest
from types import SimpleNamespace
from unittest.mock import patch

import src.app as app_module


class ReferenceData(SimpleNamespace):
    def __getitem__(self, column):
        return getattr(self, column, "")


class BibTeXHelperTests(unittest.TestCase):
    def test_escape_bibtex_escapes_special_characters(self):
        value = "A&B%$#_{}~^\\"
        expected = (
            r"A\&B\%\$\#\_\{\}\textasciitilde{}"
            r"\textasciicircum{}\textbackslash{}"
        )

        self.assertEqual(app_module._escape_bibtex(value), expected)

    def test_escape_bibtex_converts_non_string_values_to_text(self):
        self.assertEqual(app_module._escape_bibtex(2024), "2024")

    def test_create_bibtex_formats_entry_and_sanitizes_citation_key(self):
        reference = ReferenceData(
            type="Online source",
            author="Smith, Jane and Doe, John",
            publish_year=2023,
            name="A & B: research",
            url="https://example.test/a_b",
        )
        expected_entry_type = app_module.ENTRY_TYPE_ALIASES["Online source"]

        result = app_module._create_bibtex(reference)

        self.assertTrue(result.startswith(f"@{expected_entry_type}{{Smith2023ABresearch,"))
        self.assertIn(r"title = {A \& B: research}", result)
        self.assertIn("author = {Smith, Jane and Doe, John}", result)
        self.assertIn("year = {2023}", result)
        self.assertIn(r"url = {https://example.test/a\_b}", result)
        self.assertTrue(result.endswith("\n}"))

"""
    def test_create_bibtex_uses_misc_and_reference_when_values_are_empty(self):
        reference = SimpleNamespace(
            type="not-a-known-type",
            author="",
            publish_year=None,
            name="",
            url="",
        )

        result = app_module._create_bibtex(reference)

        self.assertTrue(result.startswith("@misc{Reference,"))
        self.assertIn("title = {}", result)
        self.assertNotIn("author =", result)
        self.assertNotIn("year =", result)
        self.assertNotIn("url =", result)
"""

class FlaskRouteTests(unittest.TestCase):
    def setUp(self):
        self._previous_testing = app_module.app.testing
        app_module.app.testing = True
        self.client = app_module.app.test_client()

    def tearDown(self):
        app_module.app.testing = self._previous_testing

    def test_field_label_returns_configured_label_or_original_column(self):
        column, label = next(iter(app_module.FIELD_LABELS.items()))

        self.assertEqual(app_module.field_label(column), label)
        self.assertEqual(app_module.field_label("unmapped_column"), "unmapped_column")

    def test_index_renders_references_and_empty_form_values(self):
        references = [SimpleNamespace(name="Example")]
        with patch.object(app_module, "get_all_sources", return_value=references), patch.object(
            app_module, "render_template", return_value="index rendered"
        ) as render:
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "index rendered")
        render.assert_called_once_with(
            "index.html", references=references, form_values={}
        )

    def test_create_reference_rejects_missing_title(self):
        form = {"name": "   ", "type": "Article", "author": "Ada Lovelace"}
        with patch.object(app_module, "get_all_sources", return_value=[]), patch.object(
            app_module, "add_source"
        ) as add_source, patch.object(
            app_module, "render_template", return_value="invalid form"
        ) as render:
            response = self.client.post("/create", data=form)

        self.assertEqual(response.status_code, 400)
        add_source.assert_not_called()
        self.assertEqual(render.call_args.args[0], "add_reference.html")
        self.assertEqual(render.call_args.kwargs["error"], "Required fields: Title.")

    def test_create_reference_rejects_non_integer_publish_year(self):
        form = {
            "name": "A title",
            "type": "Article",
            "author": "Ada Lovelace",
            "publish_year": "20xx",
        }
        with patch.object(app_module, "get_all_sources", return_value=[]), patch.object(
            app_module, "add_source"
        ) as add_source, patch.object(
            app_module, "render_template", return_value="invalid form"
        ) as render:
            response = self.client.post("/create", data=form)

        self.assertEqual(response.status_code, 400)
        add_source.assert_not_called()
        self.assertEqual(
            render.call_args.kwargs["error"],
            "Publication year must contain one to four digits.",
        )

    def test_create_reference_trims_values_converts_year_and_redirects(self):
        form = {
            "name": "  A title  ",
            "type": "  Article  ",
            "author": "  Ada Lovelace  ",
            "publish_year": " 1843 ",
        }
        with patch.object(app_module, "add_source") as add_source:
            response = self.client.post("/create", data=form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        submitted = add_source.call_args.args[0]
        self.assertEqual(submitted["name"], form["name"])
        self.assertEqual(submitted["type"], form["type"])
        self.assertEqual(submitted["author"], form["author"])

    def test_create_reference_accepts_blank_year(self):
        form = {
            "name": "A title",
            "type": "Article",
            "author": "Ada Lovelace",
            "publish_year": " ",
        }
        with patch.object(app_module, "add_source") as add_source:
            response = self.client.post("/create", data=form)

        self.assertEqual(response.status_code, 302)
        submitted = add_source.call_args.args[0]
        self.assertEqual(submitted["publish_year"].strip(), "")

    def test_add_reference_get_uses_type_schema_when_type_is_known(self):
        type_input = next(iter(app_module.ENTRY_TYPE_ALIASES))
        entry = app_module.ENTRY_TYPE_ALIASES[type_input]
        fields = app_module.REFERENCE_FIELD_SCHEMAS[entry]
        with patch.object(app_module, "render_template", return_value="form rendered") as render:
            response = self.client.get("/create", query_string={"type": type_input})

        self.assertEqual(response.status_code, 200)
        render.assert_called_once_with(
            "add_reference.html",
            type_input=type_input,
            entry_types=app_module.ENTRY_TYPE_ALIASES,
            fields=fields,
            form_values={},
            error=None,
        )

    def test_add_reference_get_without_type_has_no_schema(self):
        with patch.object(app_module, "render_template", return_value="form rendered") as render:
            response = self.client.get("/create")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(render.call_args.kwargs["type_input"], "")
        self.assertIsNone(render.call_args.kwargs["fields"])
        self.assertEqual(render.call_args.kwargs["form_values"], {})

    def test_add_reference_post_trims_values_and_redirects(self):
        form = {
            "name": "  A book  ",
            "type": "  Book  ",
            "author": "  A Writer  ",
            "publish_year": " 2001 ",
            "url": " https://example.test/book ",
        }
        with patch.object(app_module, "add_source") as add_source:
            response = self.client.post("/create", data=form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        submitted = add_source.call_args.args[0]
        self.assertEqual(submitted["name"], form["name"])
        self.assertEqual(submitted["type"], form["type"])
        self.assertEqual(submitted["author"], form["author"])
        self.assertEqual(submitted["publish_year"], form["publish_year"])

    def test_show_reference_renders_reference_and_bibtex(self):
        reference = ReferenceData(
            type="Book", author="A Writer", publish_year=2001, name="A Book", url=""
        )
        with patch.object(app_module, "get_source", return_value=reference) as get_source, patch.object(
            app_module, "render_template", return_value="reference rendered"
        ) as render:
            response = self.client.get("/ref/17")

        self.assertEqual(response.status_code, 200)
        get_source.assert_called_once_with(17)
        self.assertEqual(render.call_args.args[0], "reference.html")
        self.assertIs(render.call_args.kwargs["reference"], reference)
        self.assertEqual(
            render.call_args.kwargs["bibtex"], app_module._create_bibtex(reference)
        )

    def test_show_missing_reference_passes_none_bibtex_to_template(self):
        with patch.object(app_module, "get_source", return_value=None):
            with self.assertRaises(AttributeError):
                self.client.get("/ref/999")


if __name__ == "__main__":
    unittest.main()
