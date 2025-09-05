"""
Handles the extraction of highlight annotations from PDF files.
"""
import fitz  # PyMuPDF
import re
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
        if not page.annots():
            continue

        for annot in page.annots():
            if annot.type[0] == 8:  # Highlight annotation
                quads = annot.quads()
                if not quads:
                    continue

                highlighted_text = ""
                for quad in quads:
                    rect = fitz.Rect(quad.ul, quad.lr)
                    # Extract text as a single block to preserve original newlines
                    highlighted_text += page.get_text("text", clip=rect)
                
                # Clean up text: replace single newlines with spaces, but keep double newlines
                cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', highlighted_text)
                
                # Get annotation note (comment)
                info = annot.info
                note = info.get("content", "") if info else ""

                # Get highlight color
                color = None
                if annot.colors and "stroke" in annot.colors:
                    stroke_color = annot.colors.get("stroke")
                    if stroke_color and len(stroke_color) == 3:
                        color = '#%02x%02x%02x' % (int(stroke_color[0]*255), int(stroke_color[1]*255), int(stroke_color[2]*255))

                highlights.append(
                    Annotation(
                        text=cleaned_text.strip(),
                        page_number=page_num,
                        color=color,
                        note=note.strip(),
                    )
                )

    doc.close()
    return highlights
