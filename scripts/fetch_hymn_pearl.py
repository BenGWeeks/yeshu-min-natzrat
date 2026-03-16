"""Fetch the Hymn of the Pearl from gnosis.org (G.R.S. Mead translation).

Converts to USFM (sources/) then generates AsciiDoc (appendices/).
Note: gospels.net does not carry this text. gnosis.org hosts the
pre-1923 Mead translation which is public domain.
"""

import re
from pathlib import Path
from common import fetch_html, get_gnosis_content
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
APPENDICES_DIR = PROJECT_DIR / "appendices"

URL = "http://www.gnosis.org/library/hymnpearl.htm"

INTRO = (
    "The Hymn of the Pearl (also called the Hymn of the Soul) is embedded within "
    "the Acts of Thomas, a 3rd-century text about the apostle Thomas\u2019s journey "
    "to India. The hymn itself may be older than its narrative frame."
    "\n\n"
    "It tells the story of a prince sent from the Kingdom of Light into Egypt to "
    "retrieve a pearl guarded by a serpent. In Egypt, the prince forgets his identity "
    "and his mission. A letter from home awakens him. He retrieves the pearl, puts on "
    "his robe of glory, and returns to his Father\u2019s Kingdom."
    "\n\n"
    "This is the canon\u2019s creation myth: the soul descends into matter, forgets its "
    "divine origin, is awakened by the teaching, and returns home. The Gospel of Thomas "
    "points toward the same truth from within: \u201cIf they say to you, \u2018Where did you "
    "come from?\u2019, say to them, \u2018We came from the light.\u2019\u201d"
)

ATTRIBUTION = "Translation by G.R.S. Mead \u2014 public domain (pre-1923)."

# Roman numeral to int mapping for stanza numbers
ROMAN_RE = re.compile(r"^([IVXLCDM]+)\.$")
ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
    "XXI": 21, "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25,
}


def fetch_and_convert():
    """Fetch Hymn of the Pearl and convert to USFM then AsciiDoc."""
    soup = fetch_html(URL)
    content = get_gnosis_content(soup)
    text = content.get_text("\n")
    lines_raw = [l.strip() for l in text.split("\n")]

    # Find the poem: starts after "Translated by G.R.S. Mead" with "I."
    chapters = []
    current_stanza = None
    current_lines = []
    line_counter = 0
    in_poem = False

    for line in lines_raw:
        if not in_poem:
            if line == "I.":
                in_poem = True
                current_stanza = 1
                current_lines = []
                line_counter = 0
            continue

        # Stop at second translation or footer
        if any(stop in line for stop in [
            "William Wright", "second translation", "Apocryphal Acts",
            "Return to", "Archive |",
        ]):
            break

        # Check for stanza number
        roman_match = ROMAN_RE.match(line)
        if roman_match:
            # Save previous stanza
            if current_stanza is not None and current_lines:
                chapters.append({
                    "number": current_stanza,
                    "heading": f"Stanza {current_stanza}",
                    "verses": current_lines,
                    "poetry": True,
                })
            roman = roman_match.group(1)
            current_stanza = ROMAN_MAP.get(roman, current_stanza + 1)
            current_lines = []
            line_counter = 0
            continue

        # Skip empty lines
        if not line:
            continue

        # Poem line
        line_counter += 1
        current_lines.append({"number": line_counter, "text": line})

    # Save last stanza
    if current_stanza is not None and current_lines:
        chapters.append({
            "number": current_stanza,
            "heading": f"Stanza {current_stanza}",
            "verses": current_lines,
            "poetry": True,
        })

    # Write USFM
    usfm_path = SOURCES_DIR / "HYP.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="HYP",
        title="The Hymn of the Pearl",
        short_title="Hymn of the Pearl",
        abbreviation="HyP",
        chapters=chapters,
    )

    # Generate AsciiDoc
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
        subtitle="From the Acts of Thomas",
        poetry_format=True,
    )
    adoc_path = APPENDICES_DIR / "hymn-of-the-pearl.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    APPENDICES_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Hymn of the Pearl...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
