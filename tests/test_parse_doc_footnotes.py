import importlib.resources
from pathlib import Path

from bookpull.main import parse_footnotes

RESOURCES = importlib.resources.files("tests.resources")


def test_parse_sample_article_footnotes_cout():
    article_path = RESOURCES / "sample-article.docx"
    footnotes = parse_footnotes(article_path)
    for i, note in enumerate(footnotes, start=1):
        print(f"Footnote {i}: {note.text}")
    assert len(footnotes) == 453


def test_parse_small_doc_footnotes_content():
    assert_parse_footnotes(
        "small-doc.docx",
        ["Note 1", "Note 2", "This is the third footnote"],
    )


def test_parse_sample_paragraph_footnotes_content():
    assert_parse_footnotes(
        "sample-article-paragraph.docx",
        [
            (
                "389 U.S. 347 (1967); see, e.g., Kiel Brennan-Marquez, "
                "Outsourced Law Enforcement, 18 U. Pa. J. Const. L. 797, 801 "
                "(2016) (noting that Katz “ushered in the modern era of Fourth"
                " Amendment law”)."
            ),
            "See Katz, 389 U.S. at 360-62 (Harlan, J., concurring).",
            (
                "See United States v. Jones, 565 U.S. 400 (2012); Florida v."
                " Jardines, 569 U.S. 1 (2013); Carpenter v. United States, "
                "138 S. Ct. 2206, 2261 (2018) (Gorsuch, J., dissenting); see "
                "also Carpenter, 138 S. Ct. at 2224 (Kennedy, J., dissenting) "
                "(“[T]he Court unhinges Fourth Amendment doctrine from the "
                "property-based concepts that have long grounded the analytic "
                "framework that pertains in these cases.”)."
            ),
        ],
    )


def assert_parse_footnotes(file_name: str, expected_footnotes: list[str]):
    footnotes = parse_footnotes(RESOURCES / file_name)
    text = [footnotes.text for footnotes in footnotes]
    assert text == expected_footnotes
