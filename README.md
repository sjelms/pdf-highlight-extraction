# pdf-highlight-extraction

A Python tool to extract highlighted text from PDF documents using the PyMuPDF library (fitz). This project enables users to programmatically retrieve text annotations, their positions, and metadata from PDFs for further analysis or processing.

## Requirements

- Python 3.7+
- PyMuPDF (`fitz`) library

Install dependencies with:

```bash
pip install pymupdf
```

## Features

- Extract highlighted text from PDF files
- Retrieve annotation coordinates and page information
- Support for multiple highlights per page
- Export highlights to **Readwise-ready CSV** and **Markdown** files

## How It Works

1. Open the PDF document using PyMuPDF.
2. Iterate through each page and find highlight annotations.
3. For each highlight, obtain the coordinates and extract the corresponding text.
4. Collect and output all highlights with their metadata.

6. Export the collected highlights into both CSV (formatted for Readwise import) and Markdown (for use in Obsidian or other note apps).

### CSV Export Details

The exported CSV file follows the [Readwise CSV import template](https://readwise.io/csv_template). The CSV includes the following seven required columns:

1. **Title** – The title of the source document (e.g., the PDF file name or document title).
2. **Author** – The author(s) of the document.
3. **Category** – Type of source, typically "books", "articles", or "supplementals".
4. **Source URL** – A URL to the source document, if available (can be blank for local PDFs).
5. **Highlight** – The highlighted text extracted from the PDF.
6. **Note** – Any note or comment associated with the highlight (can be blank if not present).
7. **Location** – The location of the highlight within the document (e.g., page number or coordinates).

#### Field Mapping: PDF Annotations to Readwise CSV

| Readwise CSV Field | PDF Annotation Source            |
|--------------------|----------------------------------|
| Title              | PDF metadata title or file name   |
| Author             | PDF metadata author               |
| Category           | User-specified or default ("books")|
| Source URL         | User-specified or blank           |
| Highlight          | Highlighted text from annotation  |
| Note               | Annotation comment or blank       |
| Location           | Page number and/or annotation position |

## Example Usage

```python
import fitz

doc = fitz.open("sample.pdf")
for page in doc:
    for annot in page.annots():
        if annot.type[0] == 8:  # Highlight annotation
            info = annot.info
            quads = annot.vertices
            text = page.get_textbox(annot.rect)
            print(f"Page {page.number + 1}: {text}")
```

Example output:

```
Page 2: This is a highlighted text from the PDF.
Page 5: Another highlight extracted successfully.
```

## Roadmap

- Full support for exporting annotations into Readwise CSV template  
- Markdown export of highlights with customizable formatting
- Integrate with GUI tools for easier PDF selection
- Improve text extraction accuracy for complex layouts
