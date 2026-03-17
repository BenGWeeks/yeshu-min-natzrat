"""Fetch Gospel of Philip Mary Magdalene extracts from gospels.net.

Converts to USFM (sources/) then generates AsciiDoc (appendices/).
"""

import re
from pathlib import Path
from common import fetch_html
from usfm import write_usfm, read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
APPENDICES_DIR = PROJECT_DIR / "appendices"

URL = "https://www.gospels.net/philip"

INTRO = (
    "The Gospel of Philip is a Valentinian Gnostic text from the late 2nd or 3rd "
    "century, discovered at Nag Hammadi. It is not a gospel in the narrative sense "
    "but a collection of theological reflections, parables, and sayings."
    "\n\n"
    "The passages extracted here concern Mary Magdalene. Philip states that Jesus "
    "\u201cloved her more than all the disciples and used to kiss her often.\u201d When the "
    "other disciples object, Jesus asks: \u201cWhy do I not love you like her?\u201d"
    "\n\n"
    "Philip also describes Mary as Jesus\u2019s \u201ccompanion\u201d (koinonos in Greek) and "
    "presents her as the recipient of special knowledge. These passages corroborate "
    "the Gospel of Mary\u2019s portrait of Mary Magdalene as the primary female disciple "
    "and a figure of greater spiritual authority than Peter."
)

ATTRIBUTION = "Translation by Mark M. Mattison \u2014 gospels.net, public domain."

MARY_KEYWORDS = [
    "mary magdalene", "magdalene", "companion",
    "loved her more", "kiss her", "kissed her",
    "three who always walked", "his sister and his mother",
    "why do i not love you", "companion of the",
    "mary is his sister", "his partner",
]


def fetch_and_convert():
    """Fetch Gospel of Philip and extract Mary Magdalene passages."""
    soup = fetch_html(URL)
    body = soup.find("body") or soup
    text = body.get_text("\n")

    # Split into paragraphs
    paragraphs = []
    current_para = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
        else:
            current_para.append(line)
    if current_para:
        paragraphs.append(" ".join(current_para))

    # Find Mary passages
    skip_patterns = [
        "gospels.net", "public domain", "copyright", "toggle navigation",
        "home", "about", "translations", "cookie", "privacy",
        "mark m. mattison", "gospel of philip",
    ]

    mary_passages = []
    for para in paragraphs:
        if any(kw in para.lower() for kw in MARY_KEYWORDS):
            if any(skip in para.lower() for skip in skip_patterns):
                continue
            if len(para) > 30:
                mary_passages.append(para)

    # Write USFM (Mary extracts only)
    verses = []
    for i, passage in enumerate(mary_passages, 1):
        verses.append({"number": i, "text": passage})

    chapters = [{
        "number": 1,
        "heading": None,
        "verses": verses,
        "poetry": False,
    }]

    usfm_path = SOURCES_DIR / "GPH-MARY.usfm"
    write_usfm(
        filepath=usfm_path,
        book_id="GPH",
        title="Gospel of Philip (Mary Passages)",
        short_title="Philip (Mary)",
        abbreviation="GPh",
        chapters=chapters,
    )

    # Generate AsciiDoc
    usfm_data = read_usfm(usfm_path)
    adoc = usfm_to_adoc(
        usfm_data,
        intro=INTRO,
        attribution=ATTRIBUTION,
    )
    adoc_path = APPENDICES_DIR / "gospel-of-philip-mary.adoc"
    adoc_path.write_text(adoc, encoding="utf-8")
    print(f"  AsciiDoc saved to {adoc_path}")


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    APPENDICES_DIR.mkdir(parents=True, exist_ok=True)
    print("Processing Gospel of Philip (Mary passages)...")
    fetch_and_convert()


if __name__ == "__main__":
    main()
