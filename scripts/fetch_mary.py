"""Fetch the Gospel of Mary from gospels.net (Mattison translation).

Converts to USFM (sources/) then generates AsciiDoc (chapters/).
"""

import re
from pathlib import Path
from common import fetch_html
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
CHAPTERS_DIR = PROJECT_DIR / "chapters"

URL = "https://www.gospels.net/mary"

INTRO = (
    "The Gospel of Mary survives in fragmentary form \u2014 pages 1\u20136 and 11\u201314 "
    "are missing from the sole Coptic manuscript. What remains presents Mary Magdalene "
    "as the disciple who received teaching the others did not get. She describes a "
    "vision of the soul\u2019s ascent past the powers that bind it to the material world."
    "\n\n"
    "Peter challenges her: \u201cDid he really speak with a woman without our knowledge?\u201d "
    "Levi rebukes Peter: \u201cIf the Saviour made her worthy, who are you to reject her?\u201d"
    "\n\n"
    "The missing pages almost certainly contained the core of Jesus\u2019s private teaching "
    "to Mary. Their destruction \u2014 whether by time or by deliberate suppression \u2014 is "
    "one of the great losses of early Christian literature."
)

ATTRIBUTION = "Translation by Mark M. Mattison \u2014 gospels.net, public domain."

# Known section headings on gospels.net
SECTION_HEADINGS = {
    "an eternal perspective", "the gospel", "mary and jesus",
    "overcoming the powers", "conflict over authority",
}


def fetch_and_convert():
    """Fetch Gospel of Mary and convert to USFM then AsciiDoc."""
    soup = fetch_html(URL)
    body = soup.find("body") or soup
    text = body.get_text("\n")
    lines_raw = [l.strip() for l in text.split("\n") if l.strip()]

    # Find where actual text starts (after "Pages 1 through 6 are missing.")
    chapters = []
    current_page = None
    current_verses = []
    verse_counter = 0
    in_text = False

    skip_nav = [
        "welcome", "sayings of jesus", "gospel of thomas",
        "gospel of mary", "gospel of judas", "gospel of philip",
        "gospel of truth", "gospel of peter", "unknown gospel",
        "gospel of q", "secret book", "infancy gospel",
        "stranger's book", "secret gospel", "odes of solomon",
        "manuscript information", "note from andrew", "contact",
        "bookstore", "menu", "by mark m. mattison",
        "the following translation", "committed to the public domain",
        "pdf version", "luminescence", "earns commissions",
        "symbols", "page number", "gap in the text",
        "editorial correction", "editorial insertion",
        "for some reflections", "fresh translation",
    ]

    for line in lines_raw:
        # Skip navigation/header content
        if not in_text:
            if any(skip in line.lower() for skip in skip_nav):
                continue
            # Look for "Pages 1 through 6 are missing"
            if "pages 1 through 6 are missing" in line.lower():
                in_text = True
                # Note the missing pages
                continue
            continue

        # Detect page numbers (standalone single or double digit)
        if re.match(r"^\d{1,2}$", line):
            page_num = int(line)
            if 7 <= page_num <= 19:
                # Check if the last verse of the current page ends mid-sentence
                # (no terminal punctuation). If so, the next line continues it.
                pending_join = False
                if current_verses:
                    last_text = current_verses[-1]["text"].rstrip()
                    if last_text and last_text[-1] not in ".!?\"'\u201d\u2019)]:":
                        pending_join = True
                # Save previous page
                if current_page is not None and current_verses:
                    chapters.append({
                        "number": current_page,
                        "heading": f"Page {current_page}",
                        "verses": current_verses,
                        "poetry": False,
                        "_pending_join": pending_join,
                    })
                current_page = page_num
                current_verses = []
                verse_counter = 0
                continue

        # Detect section headings
        if line.lower() in SECTION_HEADINGS:
            continue  # Skip headings, we use page numbers

        # Detect "Pages X through Y are missing"
        if "pages" in line.lower() and "missing" in line.lower():
            verse_counter += 1
            current_verses.append({
                "number": verse_counter,
                "text": f"_[{line}]_",
            })
            continue

        # Footer detection
        if line.lower().startswith("the gospel") and len(line) < 20:
            # Could be "The Gospel" heading or "The Gospel According to"
            if "according to" in line.lower():
                break
            continue

        if any(stop in line.lower() for stop in [
            "according to mary", "according to", "copyright",
            "gospels.net", "notes on translation",
        ]):
            break

        # Regular text content
        if len(line) > 5:
            verse_counter += 1
            current_verses.append({"number": verse_counter, "text": line})

    # Save last page — truncate at colophon/notes if present
    if current_page is not None and current_verses:
        # Trim trailing notes/colophon from last page
        clean_verses = []
        for v in current_verses:
            if any(stop in v["text"].lower() for stop in [
                "according to", "notes on translation",
            ]):
                break
            clean_verses.append(v)
        if clean_verses:
            chapters.append({
                "number": current_page,
                "heading": f"Page {current_page}",
                "verses": clean_verses,
                "poetry": False,
            })

    # Post-process: join sentences that were split across page boundaries.
    # If a page was marked as _pending_join, append the first verse of the
    # next page to the last verse of that page.
    for i in range(len(chapters) - 1):
        if chapters[i].get("_pending_join") and chapters[i + 1]["verses"]:
            # Join the first verse of next page into last verse of this page
            continuation = chapters[i + 1]["verses"][0]["text"]
            chapters[i]["verses"][-1]["text"] += " " + continuation
            # Remove the joined verse from the next page
            chapters[i + 1]["verses"] = chapters[i + 1]["verses"][1:]
            # Renumber remaining verses
            for j, v in enumerate(chapters[i + 1]["verses"], 1):
                v["number"] = j

    # Clean up the _pending_join markers
    for ch in chapters:
        ch.pop("_pending_join", None)

    # Write USFM
    usfm_path = SOURCES_DIR / "MRY.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="MRY",
        title="The Gospel of Mary",
        short_title="Mary",
        abbreviation="GMy",
        chapters=chapters,
    )

    # Generate AsciiDoc
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
    )
    adoc_path = CHAPTERS_DIR / "gospel-of-mary.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Gospel of Mary...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
