"""
Handles the extraction of highlight annotations from PDF files.
"""
import fitz  # PyMuPDF
from typing import List, Optional
from pydantic import BaseModel

class Annotation(BaseModel):
    """Data model for a single highlight annotation."""
    text: str
    page_number: int
    color: Optional[str] = None
    note: Optional[str] = None

def extract_annotations(pdf_path: str) -> List[Annotation]:
    """
    Extracts highlight annotations from a PDF file.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A list of Annotation objects.
    """
    doc = fitz.open(pdf_path)
    highlights = []

    for page_num, page in enumerate(doc, start=1):
        wordlist = page.get_text("words")
        wordlist.sort(key=lambda w: (w[3], w[0]))

        for annot in page.annots():
            if annot.type[0] == 8:  # Highlight annotation
                rect = annot.rect
                highlighted_text = page.get_text("text", clip=annot.rect)

                # Get annotation note (comment)
                info = annot.info
                note = info.get("content", "") if info else ""

                # Get highlight color
                color = annot.colors.get("stroke")
                if color:
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))


                highlights.append(
                    Annotation(
                        text=highlighted_text.strip(),
                        page_number=page_num,
                        color=color,
                        note=note.strip(),
                    )
                )

    doc.close()
    return highlights
