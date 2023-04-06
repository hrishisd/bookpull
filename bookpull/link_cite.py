import re
from dataclasses import dataclass
from typing import Optional

URL_REGEX = r"https?://[^\s/$.?#].[^\s]*"
LINK_CITATION_PATTERN = re.compile(
    r"(.+),(.+) (.*)\. (.* )?\(.*\), ("  #
    + URL_REGEX
    + r") \[("
    + URL_REGEX
    + r")\]?"
)
"""Matches a link citation. The url is group 5. The permalink is group 6."""


@dataclass
class LinkCitation:
    """A link citation.

    Format:

      <Author>, <Title>, <Sposoring Org.> <pincite> (date), URL, [permalink]

    permalink is optional.
    """

    source_text: str
    url: str  # TODO: replace this with a URL type
    permalink: Optional[str]


def parse_link_citations(text: str) -> list[LinkCitation]:
    match = LINK_CITATION_PATTERN.search(text)
    if not match:
        return []
    source = match.group(0)
    url = match.group(5)
    permalink = match.group(6)
    return [LinkCitation(source_text=source, url=url, permalink=permalink)]
