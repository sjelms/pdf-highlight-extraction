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

def _quads_to_rects(vertices) -> List[fitz.Rect]:
    """Convert an annotation's quad vertices into a list of clip rects.

    PyMuPDF highlight annotations provide vertices as a flat list of points.
    Group each 4-point quad into a rectangle that can be used to clip text.
    """
    rects: List[fitz.Rect] = []
    if not vertices:
        return rects
    pts = list(vertices)
    # Case A: flat list of numbers [x0,y0,x1,y1,x2,y2,x3,y3,...]
    if pts and isinstance(pts[0], (int, float)):
        for i in range(0, len(pts), 8):
            quad = pts[i:i+8]
            if len(quad) < 8:
                break
            xs = quad[0::2]
            ys = quad[1::2]
            rects.append(fitz.Rect(min(xs), min(ys), max(xs), max(ys)))
        return rects
    # Case B: list of points [(x,y), (x,y), ...] or fitz.Point
    def _px(p):
        return getattr(p, 'x', p[0])
    def _py(p):
        return getattr(p, 'y', p[1])
    for i in range(0, len(pts), 4):
        quad_pts = pts[i:i+4]
        if len(quad_pts) < 4:
            break
        xs = [_px(p) for p in quad_pts]
        ys = [_py(p) for p in quad_pts]
        rects.append(fitz.Rect(min(xs), min(ys), max(xs), max(ys)))
    return rects


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
                # Prefer extracting text via quad rects (most reliable for highlights)
                text_parts: List[str] = []

                vertices = getattr(annot, "vertices", None)
                rects: List[fitz.Rect] = []
                if vertices:
                    rects = _quads_to_rects(vertices)

                # Fallback: some versions expose 'quads' as list of fitz.Quad
                if not rects and hasattr(annot, "quads") and annot.quads:
                    try:
                        rects = [q.rect for q in annot.quads]
                    except Exception:
                        rects = []

                # As a last resort, use the annotation's bounding rect
                if not rects and hasattr(annot, "rect") and annot.rect:
                    rects = [annot.rect]

                # Sort rects by reading order: top-to-bottom, then left-to-right
                rects.sort(key=lambda r: (round(r.y0, 2), round(r.x0, 2)))

                for r in rects:
                    try:
                        clip_text = page.get_text("text", clip=r) or ""
                    except Exception:
                        clip_text = ""
                    if clip_text:
                        text_parts.append(clip_text)

                highlighted_text = " ".join(part.strip() for part in text_parts if part.strip())

                # Clean up text: replace single newlines with spaces, but keep double newlines
                cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', highlighted_text)

                # Get annotation note (comment)
                info = annot.info
                note = info.get("content", "") if info else ""

                # Get highlight color (stroke preferred, fallback to fill)
                color = None
                try:
                    if annot.colors:
                        stroke_color = annot.colors.get("stroke")
                        fill_color = annot.colors.get("fill")
                        rgb = stroke_color or fill_color
                        if rgb and len(rgb) == 3:
                            color = '#%02x%02x%02x' % (
                                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                            )
                except Exception:
                    pass

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
