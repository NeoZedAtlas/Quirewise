# Quirewise application

Quirewise is a pure-C11 document conversion toolchain with no third-party
runtime. The `app` repository is the CLI and composition layer; every format
reader lives in an independent, installable library repository.

The typical workflow is:

```text
documents / ebooks / pages / spreadsheets / subtitles / CAD / images
                              -> PDF
PDF                           -> TXT (text extraction) or PNG (first page)
```

## What it can convert

| Family | Inputs (CLI-reachable) |
|---|---|
| Office documents | DOCX/DOCM/DOTX/DOTM, ODT/OTT/FODT, PPTX/PPTM/POTX/POTM/PPSX/PPSM, ODP/OTP/FODP, HWPX, EML |
| Ebooks | EPUB/KEPUB, MOBI 7, AZW3/MOBI 8/AZW, FB2, PMLZ, TXTZ, HTMLZ |
| Dictionaries | MDict MDX entries, with the MDD resource file as check-only input |
| Text/web | TXT, Markdown, HTML, RTF |
| Pages/scans | PDF, DjVu, PDG/PDZ, UVZ, CAJ, CEB |
| Comics | CBZ, CBT |
| Spreadsheets | XLSX/XLSM/XLTX, BIFF8 XLS/XLT, ODS/OTS/FODS, CSV/TSV |
| Structured data | JSON, JSONL, YAML, TOML, XML, vCard, OPML, iPynb |
| Subtitles | SRT, WebVTT, LRC, MicroDVD, TTML, ASS/SSA, SAMI, SCC |
| CAD/vector | DXF, DWG (R13–R2018), SVG/SVGZ (supported subset) |
| Images | JPEG, PNG, GIF, BMP, TIFF, WebP, JP2/J2K, PSD, TGA, PNM, QOI, ICO, DICOM and more |
| Audio | container/packet **check only** (`--check`), no decode or transcode |

PDF, DOCX/ODT/HTML/EPUB/FB2, PPTX/ODP, HWPX, EML, MOBI/AZW3, HTMLZ/TXTZ/PMLZ,
MDict MDX, RTF, spreadsheets, subtitles, structured data, images,
DjVu/PDZ/UVZ/CAJ/CEB, CBZ/CBT, DXF/DWG and SVG/SVGZ convert to PDF. PDF also
converts to TXT (no OCR) and PNG (first page). DXF/DWG `--to txt` emits the
drawing text inventory, and MDX `--to txt` emits one key line plus its
tag-stripped article per entry.

Besides those source-specific routes, the CLI converts inside three text
families: structured data (JSON, JSON Lines, YAML, TOML, vCard, XML), subtitles
(SRT, WebVTT, LRC, MicroDVD, ASS, SSA, SAMI, SCC) and worksheets (CSV, TSV, plus
every spreadsheet reader to CSV/TSV). Data writers cover the six listed
syntaxes; OPML and iPynb stay read-only, while XML only round-trips the ordered
XML document shape.

Layout inputs can also be written as HTML, Markdown, DOCX or EPUB. The DOCX and
EPUB outputs are deliberately minimal packages (WordprocessingML paragraphs;
one XHTML chapter plus OPF/NCX), and PDF→DOCX/EPUB reconstructs the text layer
only — layout, images and styles are not rebuilt.

See the [format capability matrix](docs/formats/support-matrix.md) for the
three-state (supported / partial / unsupported) detail.

## Requirements

- C11 compiler (MinGW-w64 or MSVC on Windows; GCC/Clang on Unix).
- CMake 3.21 or newer.
- Ninja is recommended but not required.
- No third-party runtime or codec libraries.

## Build and install

The application consumes installed Quirewise packages. A minimal conversion
build only needs the `pipeline` package, which brings the document, page,
comic, subtitle, data, CAD/SVG, audio and PDG routes through its CMake config:

```sh
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/path/to/quirewise/install \
  -DQUIREWISE_LINK_PIPELINE=ON
cmake --build build
cmake --install build --prefix /path/to/quirewise/install
```

A full composition that also reports the individual libraries:

```sh
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/path/to/quirewise/install \
  -DQUIREWISE_LINK_RUNTIME=ON \
  -DQUIREWISE_LINK_IMAGE=ON \
  -DQUIREWISE_LINK_ARCHIVE=ON \
  -DQUIREWISE_LINK_PAGE=ON \
  -DQUIREWISE_LINK_PDG=ON \
  -DQUIREWISE_LINK_DOCUMENT=ON \
  -DQUIREWISE_LINK_EBOOK=ON \
  -DQUIREWISE_LINK_TEXT=ON \
  -DQUIREWISE_LINK_DATA=ON \
  -DQUIREWISE_LINK_SPREADSHEET=ON \
  -DQUIREWISE_LINK_AUDIO=ON \
  -DQUIREWISE_LINK_SUBTITLE=ON \
  -DQUIREWISE_LINK_VECTOR=ON \
  -DQUIREWISE_LINK_COMIC=ON \
  -DQUIREWISE_LINK_PIPELINE=ON
```

Every `QUIREWISE_LINK_*` option defaults to `OFF`. A plain
`cmake -S . -B build` builds a shell that supports `--help`, `--version` and
`--libraries` only.

## Command line

```text
quirewise INPUT [INPUT ...] [options]

  -o, --out FILE            write the result to FILE
      --out-dir DIR         put default output names under DIR
      --to FORMAT           pdf (default), txt, png, json, jsonl, yaml, toml,
                            xml, vcf, srt, vtt, lrc, sub, ass, ssa, sami, scc,
                            csv, tsv, html, md, docx, epub, bmp, tiff, jpg, webp,
                            htmlz, txtz, hwpx
      --check               verify inputs can be read; write nothing
      --quiet               suppress success output
      --page MODE           raster page box: image (default) or a4
      --pages RULE          PDG page rule: auto, body, body+att, all
      --archive-password T  CBZ/CBT/7z archive password
      --audio-track N       one-based audio track for --check
      --help                show help
      --version             show the application version
      --libraries           list libraries selected at configure time
```

Behavior:

- Outputs are **never overwritten**. A failed write removes the partial file.
- The `-o` extension must match `--to` (`\.pdf`, `\.txt`, `\.png`, `\.json`,
  `\.yaml`, `\.srt`, `\.vtt`, `\.csv`, `\.html`, `\.md`, `\.docx`, `\.epub`, `\.bmp`, `\.tiff`, `\.jpg`, `\.webp`, `\.htmlz`, `\.txtz`, `\.hwpx`, …).
- `--to` cannot be combined with `--check`; `-o` cannot be used with multiple
  inputs or with `--check`.
- Exit code `0` is success, `1` is a conversion/read failure, `2` is a usage
  error.
- Errors distinguish `format error`, `unsupported`, `decode error`,
  `resource limit`, `I/O error`, `empty input` and related statuses.
- A partially readable page container warns and keeps the readable pages; with
  `--check` it fails instead.
- Audio inputs are accepted only by `--check` (container/packet parse).

## Examples

Convert a document or ebook:

```sh
quirewise report.docx
quirewise book.epub --out-dir out
quirewise book.epub --page a4 -o book-a4.pdf
```

Batch conversion:

```sh
quirewise *.pdf *.png *.jpg --out-dir converted
```

Verify without writing:

```sh
quirewise scan.pdz book.cbz sample.ttml --check
quirewise track.wav --check --audio-track 1
```

PDF outputs:

```sh
quirewise manual.pdf --to txt -o manual.txt
quirewise manual.pdf --to png -o cover.png
```

Family conversions:

```sh
quirewise notes.json --to yaml -o notes.yaml
quirewise captions.srt --to vtt -o captions.vtt
quirewise sheet.xlsx --to csv -o sheet.csv
quirewise report.docx --to html -o report.html
quirewise report.docx --to md -o report.md
quirewise report.docx --to docx -o copy.docx
quirewise report.docx --to epub -o book.epub
quirewise cover.png --to bmp -o cover.bmp
quirewise scan.tiff --to png -o scan.png
quirewise photo.bmp --to jpg -o photo.jpg
quirewise diagram.png --to webp -o diagram.webp
quirewise report.docx --to htmlz -o report.htmlz
quirewise notes.txt --to txtz -o notes.txtz
quirewise report.md --to hwpx -o report.hwpx
```

CAD text inventory:

```sh
quirewise drawing.dwg --to txt -o drawing.txt
```

Page containers:

```sh
quirewise book.pdz --pages auto
quirewise book.pdz --pages all -o book-all.pdf
quirewise encrypted.cbz --archive-password secret
```

## Composition model

There are 18 independent library repositories plus the application and the
external consumer template:

`runtime`, `charset`, `compression`, `crypto`, `image`, `archive`, `page`,
`pdg`, `document`, `ebook`, `text`, `data`, `spreadsheet`, `audio`, `subtitle`,
`vector`, `comic`, `pipeline`.

`pipeline` is a composition package: it depends on the installed readers and
provides the document-first fallback chain used by the CLI. The application
does not compile a nested copy of any library. See
[the application shell source](src/main.c) and the pipeline repository for the
public composition API.

## Validate the workspace

Build/test all libraries, the external consumer and the application, then run
the boundary gates:

```sh
python tools/run_acceptance.py --workspace ..
```

Useful narrower loops:

```sh
python tools/run_acceptance.py --workspace .. --shared
python tools/run_acceptance.py --workspace .. --skip-consumer --skip-app
```

Validate the dependency graph alone:

```sh
python tools/validate_dependency_graph.py --workspace ..
```

The same check is available as a CMake target with
`-DQUIREWISE_VALIDATE_DEPENDENCIES=ON`.

## Release checks

- `tools/audit_release_boundaries.py` — third-party header/symbol/CMake denylist
- `tools/audit_mupdf_removal.py` — legacy MuPDF boundary removal
- `tools/verify_public_headers.py` / `tools/verify_header_isolation.py` —
  public-header independence
- `tools/verify_header_ownership.py` — no two packages install different bytes
  at the same public-header path
- `tools/check_consumer_coverage.py` — exported API to consumer call mapping
- `tools/generate_sbom.py` — CycloneDX SBOM, license inventory and installed
  prefix manifest
- `tools/verify_pdf_pages.c` — render-based PDF check (blank/solid pages,
  unknown image filters)
- `tools/audit_vendored_sources.py` — vendored-source allowlist gate

## Documentation

- [Command line reference](docs/usage/command-line.md)
- [Format capability matrix](docs/formats/support-matrix.md)
- [Documents and text](docs/formats/documents-and-text.md)
- [PDF and pages](docs/formats/pdf-and-pages.md)
- [Spreadsheets, data and subtitles](docs/formats/spreadsheets-data-subtitles.md)

## License

MIT. See [LICENSE](LICENSE). Every library and the external consumer template
carry the same MIT grant.
