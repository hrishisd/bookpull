from bookpull.link_cite import (
    LINK_CITATION_PATTERN,
    LinkCitation,
    parse_link_citations,
)


def test_parse_link_citations_no_match():
    """Test parsing a string with no link citations."""
    text = ":See Katz, 389 U.S. at 360-62 (Harlan, J., concurring)."
    link_citations = parse_link_citations(text)
    assert link_citations == []


def test_parse_link_citations_single_with_permalink():
    """Test parsing a single link citation that includes a permalink."""
    text = (
        "See Randy E. Barnett, Kavanaugh Testimony, Part 1: On Originalism, Volokh Conspiracy (Sept. 14, 2018), "  # noqa: E501
        "https://reason.com/volokh/2018/09/14/kavanaugh-testimony-part-1-on-originalis [https://perma.cc/WA8R-3SAV]"  # noqa: E501
    )
    link_citations = parse_link_citations(text)
    print(f"{LINK_CITATION_PATTERN=}")
    print(f"{link_citations=}")
    assert link_citations == [
        LinkCitation(
            source_text=text,
            url="https://reason.com/volokh/2018/09/14/kavanaugh-testimony-part-1-on-originalis",  # noqa: E501
            permalink="https://perma.cc/WA8R-3SAV",
        )
    ]


def test_parse_link_citations_single_without_permalink():
    """Test parsing a single link citation that omits a permalink."""
    text = "See Randy E. Barnett, Kavanaugh Testimony, Part 1: On Originalism, Volokh Conspiracy (Sept. 14, 2018), https://reason.com/volokh/2018/09/14/kavanaugh-testimony-part-1-on-originalis"  # noqa: E501
    link_citations = parse_link_citations(text)
    print(f"{LINK_CITATION_PATTERN=}")
    print(f"{link_citations=}")
    assert link_citations == [
        LinkCitation(
            source_text=text,
            url="https://reason.com/volokh/2018/09/14/kavanaugh-testimony-part-1-on-originalis",  # noqa: E501
            permalink=None,
        )
    ]


def test_parse_link_citations_multiple():
    """Test parsing a string with multiple link citations."""
    pass
