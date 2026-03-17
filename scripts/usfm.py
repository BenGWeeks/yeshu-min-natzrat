"""USFM reading and writing utilities.

USFM (Unified Standard Format Markers) is the standard plain-text
markup for Bible texts. We use it as our intermediate format for all
source texts — canonical and non-canonical.
"""

import re
from pathlib import Path


def write_usfm(
    filepath: Path,
    book_id: str,
    title: str,
    short_title: str,
    abbreviation: str,
    chapters: list[dict],
) -> None:
    """Write a USFM file.

    Args:
        filepath: Output path for the .usfm file.
        book_id: USFM book identifier (e.g., "MAT", "GTH", "MRY").
        title: Full title (e.g., "The Gospel of Thomas").
        short_title: Short title for headers (e.g., "Thomas").
        abbreviation: 3-letter abbreviation (e.g., "GTh").
        chapters: List of chapter dicts with structure:
            {
                "number": int,
                "heading": str | None,  # Optional section heading
                "verses": [{"number": int, "text": str}],
                "poetry": bool,  # If True, format as poetry lines
            }
    """
    lines = []
    lines.append(f"\\id {book_id} {title}")
    lines.append("\\ide UTF-8")
    lines.append(f"\\h {short_title}")
    lines.append(f"\\toc1 {title}")
    lines.append(f"\\toc2 {short_title}")
    lines.append(f"\\toc3 {abbreviation}")
    lines.append(f"\\mt1 {title}")

    for ch in chapters:
        lines.append(f"\\c {ch['number']}")

        if ch.get("heading"):
            lines.append(f"\\s1 {ch['heading']}")

        is_poetry = ch.get("poetry", False)

        if not is_poetry:
            lines.append("\\p")

        for v in ch.get("verses", []):
            text = v["text"]
            if is_poetry:
                lines.append(f"\\q1")
                lines.append(f"\\v {v['number']} {text}")
            else:
                lines.append(f"\\v {v['number']} {text}")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  USFM written to {filepath}")


def read_usfm(filepath: Path) -> dict:
    """Read a USFM file and return structured data.

    Returns:
        {
            "id": str,
            "title": str,
            "short_title": str,
            "abbreviation": str,
            "chapters": [
                {
                    "number": int,
                    "heading": str | None,
                    "verses": [{"number": int, "text": str}],
                    "poetry": bool,
                }
            ],
        }
    """
    content = filepath.read_text(encoding="utf-8")

    result = {
        "id": "",
        "title": "",
        "short_title": "",
        "abbreviation": "",
        "chapters": [],
    }

    current_chapter = None
    is_poetry = False

    for line in content.split("\n"):
        line = line.rstrip()

        if line.startswith("\\id "):
            parts = line[4:].split(" ", 1)
            result["id"] = parts[0]
            if len(parts) > 1:
                result["title"] = parts[1]

        elif line.startswith("\\h "):
            result["short_title"] = line[3:].strip()

        elif line.startswith("\\toc1 "):
            result["title"] = line[6:].strip()

        elif line.startswith("\\toc3 "):
            result["abbreviation"] = line[6:].strip()

        elif line.startswith("\\mt1 "):
            if not result["title"]:
                result["title"] = line[5:].strip()

        elif line.startswith("\\c "):
            ch_num = int(line[3:].strip())
            current_chapter = {
                "number": ch_num,
                "heading": None,
                "verses": [],
                "poetry": False,
            }
            result["chapters"].append(current_chapter)
            is_poetry = False

        elif line.startswith("\\s1 ") and current_chapter is not None:
            current_chapter["heading"] = line[4:].strip()

        elif line.startswith("\\q"):
            if current_chapter is not None:
                current_chapter["poetry"] = True
                is_poetry = True

        elif line.startswith("\\v ") and current_chapter is not None:
            match = re.match(r"\\v\s+(\d+)\s+(.*)", line)
            if match:
                vnum = int(match.group(1))
                vtext = match.group(2).strip()
                current_chapter["verses"].append({
                    "number": vnum,
                    "text": vtext,
                })

        elif line.startswith("\\p"):
            is_poetry = False

    return result


def strip_usfm_inline(text: str) -> str:
    """Strip all USFM inline markup from text, leaving clean prose.

    Handles: \\w word|strong="G1234"\\w*, \\+w nested\\+w*,
    \\wj (words of Jesus), \\f footnotes\\f*, \\x cross-refs\\x*,
    and any other inline markers.
    """
    # Convert footnotes to AsciiDoc format first
    text = re.sub(
        r"\\f\s+\+\s+\\fr\s+[\d:.]+\s+\\ft\s+(.*?)\\f\*",
        r"footnote:[\1]",
        text,
    )
    # Remove cross-references
    text = re.sub(r"\\x\s+.*?\\x\*", "", text)
    # Remove \+w word|strong="G1234"\+w* (nested word markers, USFM 3.0)
    text = re.sub(r"\\\+w\s+([^|]*?)\|[^\\]*?\\\+w\*", r"\1", text)
    # Remove \w word|strong="G1234"\w* — keep just the word
    text = re.sub(r"\\w\s+([^|]*?)\|[^\\]*?\\w\*", r"\1", text)
    # Remove \wj ... \wj* (words of Jesus markers)
    text = re.sub(r"\\wj\*", "", text)
    text = re.sub(r"\\wj\s*", "", text)
    # Remove any remaining inline/character markers and their closing *
    text = re.sub(r"\\\+?[a-z]+\d?\*?", "", text)
    # Remove stray lone * left from USFM closing markers (e.g., \wj*)
    # These appear as trailing " *" or standalone "*" after stripping
    text = re.sub(r"\s+\*\s*$", "", text)
    text = re.sub(r"\s+\*\s+", " ", text)
    # Convert editorial conventions from source translations:
    # /word\ = scribal correction → (word)
    # <word> = reconstructed text → (word)
    text = re.sub(r"/([^\\]+)\\", r"(\1)", text)
    text = re.sub(r"<([^>]+)>", r"(\1)", text)
    # Clean up spacing
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text.strip()


def usfm_to_adoc(
    usfm_data: dict,
    intro: str,
    attribution: str,
    subtitle: str | None = None,
    saying_format: bool = False,
    poetry_format: bool = False,
) -> str:
    """Convert parsed USFM data to AsciiDoc.

    Args:
        usfm_data: Output from read_usfm().
        intro: Introduction paragraph for the text.
        attribution: Translation attribution line.
        subtitle: Optional subtitle under the title.
        saying_format: If True, format verses as "Saying N." instead of superscript.
        poetry_format: If True, format as verse block.

    Returns:
        AsciiDoc string.
    """
    lines = []

    # Title
    lines.append(f"== {usfm_data['title']}")
    if subtitle:
        lines.append(f"_{subtitle}_")
    lines.append("")
    lines.append("****")
    lines.append(intro)
    lines.append("")
    lines.append(attribution)
    lines.append("****")
    lines.append("")

    chapters = usfm_data["chapters"]
    multi_chapter = len(chapters) > 1

    for ch in chapters:
        # Chapter heading
        if multi_chapter and ch.get("heading"):
            lines.append(f"=== {ch['heading']}")
            lines.append("")
        elif multi_chapter:
            lines.append(f"=== Chapter {ch['number']}")
            lines.append("")

        is_poetry = ch.get("poetry", False) or poetry_format

        for v in ch["verses"]:
            text = strip_usfm_inline(v["text"])
            if saying_format:
                lines.append(f"*Saying {v['number']}.* {text}")
                lines.append("")
            elif is_poetry:
                lines.append(f"{text} +")
            else:
                lines.append(f"^{v['number']}^ {text}")

        lines.append("")

    return "\n".join(lines)
