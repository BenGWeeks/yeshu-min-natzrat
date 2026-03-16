# Yeshu min Natzrat

**A versioned, compiled canon of the earliest recoverable teachings of Jesus.**

"Yeshu min Natzrat" means "Jesus of Nazareth" in Aramaic -- his name in his own language.

**Canon version: v1.0**

## What This Is

This project assembles the ancient texts most likely to preserve what Jesus actually taught, filtered for:

- **Independence from Paul** -- no Pauline theology, no atonement framework, no cosmic Christ
- **Early date** -- first and early second century where possible
- **Proximity to the historical figure** -- family members, named disciples, community practices

The result is a single book, typeset for print (Amazon KDP hardcover), containing only the texts that meet these criteria.

## Canon Structure

### Part I: The Sayings Tradition
- **The Gospel of Thomas** (~50-120 CE) -- 114 sayings of Jesus, no narrative. Translation by Mark M. Mattison (gospels.net).
- **The Sermon on the Mount** (Matthew 5-7, Q source ~50-70 CE) -- the longest continuous block of Jesus's teaching. World English Bible (WEB).

### Part II: The Inner Teaching
- **The Gospel of Mary** (~120-150 CE) -- Mary Magdalene as primary recipient of Jesus's private teaching. Translation by Mark M. Mattison (gospels.net).
- **The Apocryphon of James** (~100-150 CE) -- secret teaching given to James and Peter. Translation by Mark M. Mattison (gospels.net).

### Part III: The Jerusalem Tradition
- **The Letter from James** (~50-70 CE) -- written by Jesus's brother. Faith without works is dead. World English Bible (WEB).
- **The Letter from Jude** (~50-90 CE) -- written by Jesus's brother, quotes 1 Enoch. World English Bible (WEB).

### Part IV: The Love Tradition
- **1 John** (~90-110 CE) -- "God is love." Independent of Paul. World English Bible (WEB).
- **2 John** (~90-110 CE) -- the Elder's brief letter on love and truth. World English Bible (WEB).
- **3 John** (~90-110 CE) -- the Elder's letter on hospitality. World English Bible (WEB).

### Part V: Community Practice
- **The Didache** (~50-120 CE) -- earliest surviving Christian community manual. Roberts-Donaldson translation (1885).

### Appendices
- **The Hymn of the Pearl** (from the Acts of Thomas) -- the soul's descent into matter and return to the Father.
- **Gospel of Philip: Mary Magdalene Passages** -- corroborating Mary Magdalene's role. Translation by Mark M. Mattison (gospels.net).

### Further Reading
- Annotated guide to related ancient texts not included in this canon.

## Translation Sources

| Source | Texts |
|--------|-------|
| Mark M. Mattison (gospels.net, public domain) | Gospel of Thomas, Gospel of Mary, Apocryphon of James, Gospel of Philip passages |
| World English Bible (WEB, public domain) | Sermon on the Mount, James, Jude, 1-3 John |
| Roberts-Donaldson (1885, public domain) | Didache |

All translations used are in the public domain.

## Build Instructions

The book is built using [asciidoctor-pdf](https://docs.asciidoctor.org/pdf-converter/latest/).

```bash
# Install asciidoctor-pdf (requires Ruby)
gem install asciidoctor-pdf

# Build the PDF
asciidoctor-pdf book.adoc -a pdf-themesdir=themes -a pdf-theme=yeshu-theme -o yeshu-min-natzrat.pdf
```

The output is `yeshu-min-natzrat.pdf`.

## Pipeline

```
Source websites (gnosis.org, gospels.net, ebible.org)
        |
        v
  fetch scripts (scripts/)
        |
        v
  USFM files (sources/*.usfm)
        |
        v
  AsciiDoc chapters (chapters/*.adoc)
        |
        v
  book.adoc (master document with includes)
        |
        v
  asciidoctor-pdf
        |
        v
  book.pdf (print-ready for Amazon KDP)
```

## Fetch Scripts

The `scripts/` directory contains Python scripts for fetching source texts:

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Fetch all source texts
python scripts/fetch_all.py
```

Individual fetch scripts exist per text (e.g., `fetch_thomas.py`, `fetch_mary.py`). The `usfm.py` module handles USFM format conversion.

## License

The ancient texts in this canon are in the **public domain** -- they belong to no one and to everyone.

Original foreword and editorial content is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Contributing

Contributions are welcome via:

- **Issues** -- report errors in transcription, suggest corrections, flag formatting problems
- **Discussions** -- propose texts for inclusion or exclusion in future canon versions, discuss translation choices, debate editorial decisions

This is a versioned canon. Changes to which texts are included constitute a new version.
