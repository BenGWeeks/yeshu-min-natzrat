"""Fetch the Didache (Roberts-Donaldson 1885 translation).

Converts to USFM (sources/) then generates AsciiDoc (chapters/).
"""

import re
from pathlib import Path
from common import fetch_html
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
CHAPTERS_DIR = PROJECT_DIR / "chapters"

URL = "http://www.earlychristianwritings.com/text/didache-roberts.html"

INTRO = (
    "The Didache (\u201cThe Teaching\u201d) is the earliest surviving Christian community "
    "manual, likely dating to the late first or early second century. It was lost for "
    "centuries and rediscovered in 1873 in a monastery in Constantinople."
    "\n\n"
    "It opens with the \u201cTwo Ways\u201d \u2014 the Way of Life and the Way of Death \u2014 and "
    "provides practical instructions for baptism, fasting, prayer, and community life. "
    "It contains a version of the Lord\u2019s Prayer and instructions for the Eucharist "
    "that predate all known liturgies."
    "\n\n"
    "The Didache is remarkable for what it does not contain: no atonement theology, "
    "no Pauline framework, no cosmic Christ. Its Christianity is purely ethical \u2014 "
    "a community trying to live by Jesus\u2019s actual teaching."
)

ATTRIBUTION = "Roberts-Donaldson translation (1885) \u2014 public domain."

ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16,
}


def fetch_and_convert():
    """Fetch Didache and convert to USFM then AsciiDoc."""
    soup = fetch_html(URL)
    body = soup.find("body") or soup
    text = body.get_text("\n")
    lines_raw = [l.strip() for l in text.split("\n")]

    chapters = []
    current_chapter = 0
    current_verses = []
    verse_counter = 0
    in_content = False

    for line in lines_raw:
        if not line:
            continue

        # Skip navigation/footer
        if any(skip in line.lower() for skip in [
            "early christian writings", "encyclopaedia", "copyright",
            "return to", "encyclopedia",
        ]):
            continue

        # Chapter markers
        ch_match = re.match(r"^Chapter\s+(\d+|[IVXLCDM]+)", line, re.IGNORECASE)
        if ch_match:
            # Save previous chapter
            if current_chapter > 0 and current_verses:
                chapters.append({
                    "number": current_chapter,
                    "heading": None,
                    "verses": current_verses,
                    "poetry": False,
                })

            ch = ch_match.group(1)
            try:
                current_chapter = int(ch)
            except ValueError:
                current_chapter = ROMAN_MAP.get(ch.upper(), current_chapter + 1)
            current_verses = []
            verse_counter = 0
            in_content = True
            continue

        if not in_content:
            continue

        # Verse numbering - look for "N." at start of line
        verse_match = re.match(r"^(\d+)\.\s+(.*)", line)
        if verse_match:
            vnum = int(verse_match.group(1))
            vtext = verse_match.group(2)
            current_verses.append({"number": vnum, "text": vtext})
        elif len(line) > 10:
            verse_counter += 1
            current_verses.append({"number": verse_counter, "text": line})

    # Save last chapter
    if current_chapter > 0 and current_verses:
        chapters.append({
            "number": current_chapter,
            "heading": None,
            "verses": current_verses,
            "poetry": False,
        })

    # Write USFM
    usfm_path = SOURCES_DIR / "DID.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="DID",
        title="The Didache",
        short_title="Didache",
        abbreviation="Did",
        chapters=chapters,
    )

    # Generate AsciiDoc
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
        subtitle="The Teaching of the Twelve Apostles",
    )
    adoc_path = CHAPTERS_DIR / "didache.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Didache...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
