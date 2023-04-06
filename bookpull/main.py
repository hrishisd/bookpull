import csv
import itertools
import typing
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import eyecite
from eyecite.models import (
    CitationBase,
    FullCaseCitation,
    FullJournalCitation,
    FullLawCitation,
    IdCitation,
    ShortCaseCitation,
    SupraCitation,
    UnknownCitation,
)

from bookpull.link_cite import LinkCitation, parse_link_citations


@dataclass
class Footnote:
    """A footnote.

    Attributes:
        num: The footnote's number. Footnote are numbered with consecutive
             integers starting from 1.
        text: The footnote's text.

    """

    num: int
    text: str


FOOTNOTE_NAMESPACE = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def parse_footnotes(doc_path: Path) -> list[Footnote]:
    """Parse footnotes from a .docx file."""
    with zipfile.ZipFile(doc_path.absolute(), "r") as archive:
        if "word/footnotes.xml" not in archive.namelist():
            raise ValueError("No footnotes found in document.")

        with archive.open("word/footnotes.xml") as footnotes_file:
            tree = ET.parse(footnotes_file)
            root = tree.getroot()

            footnote_strings = []
            for footnote in root.findall("w:footnote", FOOTNOTE_NAMESPACE):
                # footnote_type = footnote.get(
                #     f"{{{FOOTNOTE_NAMESPACE['w']}}}type"
                # )
                # if footnote_type in ["separator", "continuationSeparator"]:
                #     continue

                footnote_text = ""
                for paragraph in footnote.findall("w:p", FOOTNOTE_NAMESPACE):
                    for run in paragraph.findall("w:r", FOOTNOTE_NAMESPACE):
                        for text in run.findall("w:t", FOOTNOTE_NAMESPACE):
                            if text.text is not None:
                                footnote_text += text.text

                footnote_text = footnote_text.strip()
                if footnote_text:
                    footnote_strings.append(footnote_text)

    return [
        Footnote(num=i, text=text)
        for i, text in enumerate(footnote_strings, start=1)
    ]


def parse_citations(
    footnotes: list[Footnote],
) -> list[tuple[Footnote, list[CitationBase]]]:
    return [
        (
            footnote,
            eyecite.get_citations(
                eyecite.clean_text(footnote.text, steps=["all_whitespace"])
            ),
        )
        for footnote in footnotes
    ]


def discover_link_citations(
    citations_by_footnote: list[tuple[Footnote, list[CitationBase]]]
) -> list[tuple[Footnote, list[CitationBase | LinkCitation]]]:
    @typing.no_type_check
    def discover_links(
        footnote: Footnote, citations: list[CitationBase]
    ) -> list[CitationBase | LinkCitation]:
        if not citations:
            if link_citation := parse_link_citations(footnote.text):
                return [link_citation]
            else:
                return []
        else:
            gaps = (
                (left.full_span()[1], right.full_span()[0])
                for left, right in zip(citations, citations[1:])
            )
            link_citations: list[list[LinkCitation]] = [
                parse_link_citations(footnote.text[slice(*gap)])
                for gap in gaps
            ]
            flattened_citations: list[CitationBase | LinkCitation] = [
                elem
                for citation, link_citations in itertools.zip_longest(
                    citations, link_citations, fillvalue=[]
                )
                for elem in [
                    cast(CitationBase, citation),
                    *cast(LinkCitation, link_citations),
                ]
            ]
            return flattened_citations

    return [
        (footnote, discover_links(footnote, citations))
        for footnote, citations in citations_by_footnote
    ]


def to_csv(
    citations_by_footnote: list[
        tuple[Footnote, list[CitationBase | LinkCitation]]
    ],
    out: Path,
) -> None:
    def citation_type(citation: CitationBase) -> str:
        if isinstance(citation, (ShortCaseCitation, FullCaseCitation)):
            return "Case"
        elif isinstance(citation, FullJournalCitation):
            return "Journal"
        elif isinstance(citation, IdCitation):
            return "Id"
        elif isinstance(citation, FullLawCitation):
            return "Statute"
        elif isinstance(citation, SupraCitation):
            return "Supra"
        elif isinstance(citation, UnknownCitation):
            return "Unknown"
        else:
            raise ValueError(f"Unknown citation type: {type(citation)}")

    def make_row(
        citation: CitationBase | LinkCitation, footnote_text: str
    ) -> dict[str, str]:
        if isinstance(citation, LinkCitation):
            return {
                "citation": citation.source_text,
                "type": "Link",
                "notes": citation.url,
            }
        else:
            start_idx, stop_idx = citation.full_span()
            citation_source_text = footnote_text[start_idx:stop_idx]
            return {
                "citation": citation_source_text,
                "type": citation_type(citation),
                "source": citation.corrected_citation(),
            }

    with out.open(mode="w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["footnote", "citation", "type", "source", "notes"],
        )
        writer.writeheader()
        for footnote, citations in citations_by_footnote:
            for citation_num, citation in enumerate(citations, start=1):
                row = make_row(citation, footnote.text)
                writer.writerow(
                    row | {"footnote": f"{footnote.num}.{citation_num}"}
                )


def main() -> None:
    footnotes = parse_footnotes(Path("tests/resources/sample-article.docx"))
    citations_by_footnote = discover_link_citations(parse_citations(footnotes))
    to_csv(citations_by_footnote, Path("out.csv"))


if __name__ == "__main__":
    main()
