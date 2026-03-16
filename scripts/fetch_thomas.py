"""Fetch the Gospel of Thomas from gospels.net (Mattison translation).

Converts to USFM (sources/) then generates AsciiDoc (chapters/).
"""

import re
from pathlib import Path
from common import fetch_html
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
CHAPTERS_DIR = PROJECT_DIR / "chapters"

URL = "https://www.gospels.net/thomas"

INTRO = (
    "The Gospel of Thomas is a collection of 114 sayings attributed to Jesus, "
    "discovered in 1945 at Nag Hammadi, Egypt. It contains no narrative, no miracles, "
    "no crucifixion, no resurrection. Just sayings \u2014 many with close parallels to "
    "the Q source that underlies Matthew and Luke. Thomas presents Jesus as a wisdom "
    "teacher who points toward an interior Kingdom: \u201cthe Kingdom of the Father is "
    "spread out upon the earth, and people do not see it.\u201d"
    "\n\n"
    "The text begins: \u201cThese are the secret sayings which the living Jesus spoke "
    "and which Didymos Judas Thomas wrote down.\u201d Thomas is called \u201cthe Twin\u201d "
    "(Didymos in Greek, Toma in Aramaic) \u2014 Jesus\u2019s spiritual twin, the disciple "
    "who understood most completely what Jesus was pointing at."
)

ATTRIBUTION = "Translation by Mark M. Mattison \u2014 gospels.net, public domain."


def fetch_and_convert():
    """Fetch Gospel of Thomas and convert to USFM then AsciiDoc."""
    soup = fetch_html(URL)
    body = soup.find("body") or soup
    text = body.get_text("\n")
    lines_raw = [l.strip() for l in text.split("\n") if l.strip()]

    verses = []
    current_text_lines = []
    current_num = 0
    in_text = False

    skip_nav = [
        "welcome", "gospel of thomas", "gospel of mary",
        "gospel of judas", "gospel of philip", "gospel of truth",
        "gospel of peter", "unknown gospel", "gospel of q",
        "secret book", "infancy gospel", "stranger's book",
        "secret gospel", "odes of solomon", "manuscript information",
        "note from andrew", "contact", "bookstore", "menu",
        "by mark m. mattison", "the following translation",
        "committed to the public domain", "pdf version",
        "luminescence", "earns commissions", "symbols",
        "gap in the text", "editorial insertion",
        "editorial correction", "for some reflections",
        "new translation", "sayings of jesus",
    ]

    for line in lines_raw:
        # Skip navigation/header
        if not in_text:
            if any(skip in line.lower() for skip in skip_nav):
                continue

        # Detect "Prologue" — the preamble before Saying 1
        if line.lower() == "prologue":
            in_text = True
            continue

        # Detect saying headers: "Saying N: Title"
        saying_match = re.match(r"^Saying\s+(\d+):\s+(.*)$", line)
        if saying_match:
            # Save previous saying
            if current_num > 0 and current_text_lines:
                verses.append({
                    "number": current_num,
                    "text": " ".join(current_text_lines),
                })

            current_num = int(saying_match.group(1))
            # The title (e.g., "True Meaning") is a gospels.net addition
            # — don't include it in the verse text
            current_text_lines = []
            in_text = True
            continue

        # Footer detection
        if any(stop in line.lower() for stop in [
            "copyright", "privacy policy", "cookie",
            "the gospel according to", "colophon",
        ]):
            break

        # If we're past the prologue but before saying 1, capture preamble
        if in_text and current_num == 0:
            # This is the prologue text
            if line.startswith("These are the hidden"):
                verses.append({"number": 0, "text": line})
            continue

        # Accumulate text for current saying
        if in_text and current_num > 0:
            if any(skip in line.lower() for skip in skip_nav):
                continue
            current_text_lines.append(line)

    # Save last saying
    if current_num > 0 and current_text_lines:
        verses.append({
            "number": current_num,
            "text": " ".join(current_text_lines),
        })

    # Remove prologue verse 0 if present (handle separately)
    prologue = None
    if verses and verses[0]["number"] == 0:
        prologue = verses.pop(0)

    # Write USFM
    chapters = [{
        "number": 1,
        "heading": None,
        "verses": verses,
        "poetry": False,
    }]

    usfm_path = SOURCES_DIR / "GTH.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="GTH",
        title="The Gospel of Thomas",
        short_title="Thomas",
        abbreviation="GTh",
        chapters=chapters,
    )

    # Generate AsciiDoc with prologue
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
        saying_format=True,
    )

    # Insert prologue if we have one
    if prologue:
        # Insert after the horizontal rule
        adoc = adoc.replace(
            "'''",
            f"'''\n\n__{prologue['text']}__",
            1,
        )

    adoc_path = CHAPTERS_DIR / "gospel-of-thomas.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Gospel of Thomas...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
