"""Fetch WEB (World English Bible) canonical texts from ebible.org USFM files.

Downloads the USFM zip, extracts relevant books to sources/,
then generates AsciiDoc from the USFM.
"""

import re
import zipfile
import io
import requests
from pathlib import Path
from usfm import read_usfm, usfm_to_adoc

PROJECT_DIR = Path(__file__).parent.parent
SOURCES_DIR = PROJECT_DIR / "sources"
CHAPTERS_DIR = PROJECT_DIR / "chapters"
USFM_ZIP_URL = "https://eBible.org/Scriptures/eng-web_usfm.zip"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept-Encoding": "identity",
}

# Books to extract from the USFM zip
BOOKS = {
    "sermon-on-the-mount": {
        "usfm_file": "70-MATeng-web.usfm",
        "output_usfm": "MAT05-07.usfm",
        "output_adoc": "sermon-on-the-mount.adoc",
        "chapters": [5, 6, 7],
        "title": "The Sermon on the Mount",
        "subtitle": "Matthew 5\u20137",
        "intro": (
            "The Sermon on the Mount is the longest continuous block of Jesus\u2019s "
            "teaching in the New Testament. Scholars believe much of it derives from "
            "the Q source \u2014 a hypothetical early sayings collection predating all "
            "four Gospels. It contains the Beatitudes, the Lord\u2019s Prayer, and the "
            "core of Jesus\u2019s ethical teaching: love your enemies, do not judge, "
            "treat others as you would be treated."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
    "james": {
        "usfm_file": "89-JASeng-web.usfm",
        "output_usfm": "JAS.usfm",
        "output_adoc": "james.adoc",
        "chapters": None,
        "title": "The Letter of James",
        "subtitle": None,
        "intro": (
            "The Letter of James is possibly the earliest text in the New Testament, "
            "written by or in the name of Ya\u2019akov (James) \u2014 Jesus\u2019s own brother. "
            "It says nothing about atonement, nothing about the crucifixion as cosmic "
            "sacrifice, nothing about faith alone. Instead: feed the hungry, bridle your "
            "tongue, do not show favouritism to the rich. Faith without works is dead. "
            "This is what Jesus\u2019s own family understood he taught."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
    "jude": {
        "usfm_file": "95-JUDeng-web.usfm",
        "output_usfm": "JUD.usfm",
        "output_adoc": "jude.adoc",
        "chapters": None,
        "title": "The Letter of Jude",
        "subtitle": None,
        "intro": (
            "Jude (Judas) identifies himself as \u201cbrother of James\u201d \u2014 making him "
            "another brother of Jesus. This short letter preserves the family tradition\u2019s "
            "voice and quotes directly from 1 Enoch, confirming that the Enochic tradition "
            "was authoritative for Jesus\u2019s own family. Its warning against those who "
            "\u201cpervert the grace of our God into indecency\u201d may target Paul\u2019s "
            "antinomian teaching."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
    "1-john": {
        "usfm_file": "92-1JNeng-web.usfm",
        "output_usfm": "1JN.usfm",
        "output_adoc": "1-john.adoc",
        "chapters": None,
        "title": "The First Letter of John",
        "subtitle": None,
        "intro": (
            "1 John contains the statement \u201cGod is love\u201d \u2014 perhaps the most "
            "concise summary of what Jesus actually taught. Written by \u201cthe Elder\u201d "
            "(not the apostle John), it is independent of Paul\u2019s theology. Its test "
            "of authentic faith is simple: do you love? Then you know God. Do you not "
            "love? Then you do not know God, no matter what you believe."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
    "2-john": {
        "usfm_file": "93-2JNeng-web.usfm",
        "output_usfm": "2JN.usfm",
        "output_adoc": "2-john.adoc",
        "chapters": None,
        "title": "The Second Letter of John",
        "subtitle": None,
        "intro": (
            "A brief letter from \u201cthe Elder\u201d reinforcing the love commandment "
            "and warning against those who deny that Jesus came in the flesh. Its "
            "brevity reflects the simplicity of the original message: love one another."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
    "3-john": {
        "usfm_file": "94-3JNeng-web.usfm",
        "output_usfm": "3JN.usfm",
        "output_adoc": "3-john.adoc",
        "chapters": None,
        "title": "The Third Letter of John",
        "subtitle": None,
        "intro": (
            "The shortest book in the New Testament. A personal letter from the Elder "
            "about community hospitality and the danger of leaders who love to be first. "
            "A window into early Christian community practice before institutional "
            "hierarchy hardened."
        ),
        "attribution": "World English Bible (WEB) \u2014 public domain.",
    },
}


def extract_chapters(usfm_content: str, chapter_nums: list[int] | None) -> str:
    """Extract specific chapters from a USFM file, preserving USFM format.

    If chapter_nums is None, return the entire content.
    """
    if chapter_nums is None:
        return usfm_content

    lines = usfm_content.split("\n")
    result = []
    in_chapter = False
    header_done = False

    for line in lines:
        # Always include header lines (before first \c)
        if not header_done:
            if line.startswith("\\c "):
                header_done = True
            else:
                result.append(line)
                continue

        # Chapter marker
        if line.startswith("\\c "):
            ch_num = int(line[3:].strip())
            in_chapter = ch_num in chapter_nums
            if in_chapter:
                result.append(line)
            continue

        if in_chapter:
            result.append(line)

    return "\n".join(result)


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    # Download USFM zip
    print("Downloading WEB USFM archive...")
    resp = requests.get(USFM_ZIP_URL, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    print("  Downloaded.")

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        usfm_files = {}
        for name in zf.namelist():
            usfm_files[name] = zf.read(name).decode("utf-8")

    for key, info in BOOKS.items():
        fname = info["usfm_file"]
        if fname not in usfm_files:
            print(f"  WARNING: {fname} not found in USFM archive")
            continue

        print(f"Processing {info['title']}...")

        # Extract relevant chapters and save USFM
        usfm_content = extract_chapters(usfm_files[fname], info["chapters"])
        usfm_path = SOURCES_DIR / info["output_usfm"]
        usfm_path.write_text(usfm_content, encoding="utf-8")
        print(f"  USFM saved to {usfm_path}")

        # Generate AsciiDoc from USFM
        usfm_data = read_usfm(usfm_path)
        # Override title from USFM header with our custom title
        usfm_data["title"] = info["title"]
        adoc = usfm_to_adoc(
            usfm_data,
            intro=info["intro"],
            attribution=info["attribution"],
            subtitle=info.get("subtitle"),
        )
        adoc_path = CHAPTERS_DIR / info["output_adoc"]
        adoc_path.write_text(adoc, encoding="utf-8")
        print(f"  AsciiDoc saved to {adoc_path}")

    print("\nAll WEB texts fetched and formatted.")


if __name__ == "__main__":
    main()
