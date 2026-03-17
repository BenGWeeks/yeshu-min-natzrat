"""Fetch the Apocryphon of James from gospels.net (Mattison translation).

Converts to USFM (sources/) then generates AsciiDoc (chapters/).
"""

import re
from pathlib import Path
from common import fetch_html
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
CHAPTERS_DIR = PROJECT_DIR / "chapters"

URL = "https://www.gospels.net/james"

INTRO = (
    "The Apocryphon (Secret Book) of James presents itself as a secret teaching "
    "given by Jesus to James and Peter after the resurrection \u2014 but before the "
    "ascension. It was discovered at Nag Hammadi in 1945."
    "\n\n"
    "In this text, Jesus gives extended teaching about the Kingdom, suffering, "
    "and the nature of faith. When the other disciples ask to hear, Jesus takes "
    "only James and Peter aside. The teaching emphasises that the Kingdom requires "
    "active seeking: \u201cBe eager to be saved without being urged. Rather, be fervent "
    "on your own and, if possible, surpass even me.\u201d"
    "\n\n"
    "James \u2014 Jesus\u2019s brother \u2014 is presented as the primary recipient of this "
    "secret teaching, not Peter. This aligns with the historical evidence that James, "
    "not Peter, led the Jerusalem community."
)

ATTRIBUTION = "Translation by Mark M. Mattison \u2014 gospels.net, public domain."

# Known section headings on gospels.net for this text
SECTION_HEADINGS = {
    "salutation", "prologue", "the savior appears", "being filled",
    "the cross and death", "prophecies and parables", "the kingdom",
    "knowing the self", "becoming full", "the head of prophecy",
    "fullness and deficiency", "life and death", "the parable of the palm",
    "the parable of the grain of wheat", "the parable of the ear of grain",
    "woe and blessing", "being filled with the kingdom", "departure",
    "ascension",
}

# Navigation items to skip
SKIP_NAV = [
    "welcome", "sayings of jesus", "gospel of thomas",
    "gospel of mary", "gospel of judas", "gospel of philip",
    "gospel of truth", "gospel of peter", "unknown gospel",
    "gospel of q", "secret book of james", "infancy gospel",
    "stranger's book", "secret gospel", "odes of solomon",
    "manuscript information", "note from andrew", "contact",
    "bookstore", "menu", "by mark m. mattison",
    "the following translation", "committed to the public domain",
    "pdf version", "luminescence", "earns commissions", "symbols",
    "page number", "gap in the text", "editorial insertion",
    "editorial correction", "for some reflections",
    "the secret book of james", "the books of jesus",
    "how to be whole", "sayings of jesus: p.oxy",
]


def fetch_and_convert():
    """Fetch Apocryphon of James and convert to USFM then AsciiDoc."""
    soup = fetch_html(URL)
    body = soup.find("body") or soup
    text = body.get_text("\n")
    lines_raw = [l.strip() for l in text.split("\n") if l.strip()]

    chapters = []
    current_page = None
    current_verses = []
    verse_counter = 0
    in_text = False

    for line in lines_raw:
        # Skip navigation/header content
        if not in_text:
            if any(skip in line.lower() for skip in SKIP_NAV):
                continue
            # Content starts at "Salutation" heading
            if line.lower() == "salutation":
                in_text = True
                continue
            continue

        # Detect page numbers (standalone single digit, manuscript pages 1-16)
        if re.match(r"^\d{1,2}$", line):
            page_num = int(line)
            if 1 <= page_num <= 16:
                # Check if last verse ends mid-sentence
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

        # Skip section headings (they're editorial additions by gospels.net)
        if line.lower() in SECTION_HEADINGS:
            continue

        # Footer detection
        if any(stop in line.lower() for stop in [
            "copyright", "privacy policy", "cookie",
            "the secret book", "according to james",
            "notes on translation", "according to",
        ]):
            break

        # Set initial page if not yet set
        if current_page is None:
            current_page = 1

        # Regular text content
        if len(line) > 5:
            verse_counter += 1
            current_verses.append({"number": verse_counter, "text": line})

    # Save last page — truncate at colophon/notes
    if current_page is not None and current_verses:
        clean_verses = []
        for v in current_verses:
            if any(stop in v["text"].lower() for stop in [
                "according to", "notes on translation",
            ]):
                break
            clean_verses.append(v)
        current_verses = clean_verses if clean_verses else current_verses
        chapters.append({
            "number": current_page,
            "heading": f"Page {current_page}",
            "verses": current_verses,
            "poetry": False,
        })

    # Post-process: join sentences split across page boundaries
    for i in range(len(chapters) - 1):
        if chapters[i].get("_pending_join") and chapters[i + 1]["verses"]:
            continuation = chapters[i + 1]["verses"][0]["text"]
            chapters[i]["verses"][-1]["text"] += " " + continuation
            chapters[i + 1]["verses"] = chapters[i + 1]["verses"][1:]
            for j, v in enumerate(chapters[i + 1]["verses"], 1):
                v["number"] = j
    for ch in chapters:
        ch.pop("_pending_join", None)

    # Write USFM
    usfm_path = SOURCES_DIR / "AJA.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="AJA",
        title="The Apocryphon of James",
        short_title="Apocryphon of James",
        abbreviation="AJa",
        chapters=chapters,
    )

    # Generate AsciiDoc
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
    )
    adoc_path = CHAPTERS_DIR / "apocryphon-of-james.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Apocryphon of James...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
