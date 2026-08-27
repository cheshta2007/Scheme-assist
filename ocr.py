import io
import re
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


# ---------------------------------------------------------
# TESSERACT CONFIGURATION
# ---------------------------------------------------------

TESSERACT_PATH = "/opt/homebrew/bin/tesseract"

if Path(TESSERACT_PATH).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ---------------------------------------------------------
# IMAGE PREPROCESSING
# ---------------------------------------------------------

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare an image for better OCR accuracy.
    """

    image = image.convert("RGB")

    # Convert to grayscale
    gray = ImageOps.grayscale(image)

    # Increase contrast
    gray = ImageEnhance.Contrast(gray).enhance(1.8)

    # Sharpen text
    gray = gray.filter(ImageFilter.SHARPEN)

    # Upscale smaller documents
    width, height = gray.size

    if width < 1800:
        scale = 1800 / width
        gray = gray.resize(
            (int(width * scale), int(height * scale))
        )

    return gray


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

def perform_ocr(image: Image.Image) -> str:
    """
    Extract raw text from a document image.
    """

    processed = preprocess_image(image)

    config = "--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        processed,
        config=config,
        lang="eng"
    )

    return text.strip()


# ---------------------------------------------------------
# OCR WITH PAGE INFORMATION
# ---------------------------------------------------------

def perform_ocr_with_details(image: Image.Image) -> dict[str, Any]:
    """
    Run OCR and return text plus basic OCR metadata.
    """

    processed = preprocess_image(image)

    config = "--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        processed,
        config=config,
        lang="eng"
    )

    data = pytesseract.image_to_data(
        processed,
        config=config,
        lang="eng",
        output_type=pytesseract.Output.DICT
    )

    confidences = []

    for confidence in data["conf"]:
        try:
            value = float(confidence)

            if value >= 0:
                confidences.append(value)
        except (ValueError, TypeError):
            pass

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0
    )

    return {
        "text": text.strip(),
        "confidence": round(average_confidence, 2),
        "width": processed.width,
        "height": processed.height,
    }


# ---------------------------------------------------------
# PDF -> IMAGES
# ---------------------------------------------------------

def pdf_to_images(pdf_bytes: bytes) -> list[Image.Image]:
    """
    Convert every page of a PDF into a PIL image.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    images = []

    try:
        for page in document:
            # 2x resolution for better OCR
            matrix = fitz.Matrix(2.0, 2.0)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image = Image.open(
                io.BytesIO(pixmap.tobytes("png"))
            ).convert("RGB")

            images.append(image)

    finally:
        document.close()

    return images


# ---------------------------------------------------------
# IMAGE FILE PROCESSING
# ---------------------------------------------------------

def process_image_bytes(file_bytes: bytes) -> dict[str, Any]:
    """
    Process JPG/PNG image bytes.
    """

    image = Image.open(
        io.BytesIO(file_bytes)
    ).convert("RGB")

    result = perform_ocr_with_details(image)

    return {
        "document_type": "image",
        "pages": [
            {
                "page": 1,
                "text": result["text"],
                "confidence": result["confidence"],
            }
        ],
        "full_text": result["text"],
        "page_count": 1,
    }


# ---------------------------------------------------------
# PDF PROCESSING
# ---------------------------------------------------------

def process_pdf_bytes(file_bytes: bytes) -> dict[str, Any]:
    """
    Process a PDF page-by-page using OCR.
    """

    images = pdf_to_images(file_bytes)

    pages = []
    all_text = []

    for page_number, image in enumerate(images, start=1):

        result = perform_ocr_with_details(image)

        page_data = {
            "page": page_number,
            "text": result["text"],
            "confidence": result["confidence"],
        }

        pages.append(page_data)

        if result["text"]:
            all_text.append(result["text"])

    full_text = "\n\n".join(all_text)

    return {
        "document_type": "pdf",
        "pages": pages,
        "full_text": full_text,
        "page_count": len(pages),
    }


# ---------------------------------------------------------
# UNIVERSAL DOCUMENT PROCESSOR
# ---------------------------------------------------------

def process_document_file(
    file_bytes: bytes,
    filename: str
) -> dict[str, Any]:
    """
    Automatically detect PDF/image and run OCR.
    """

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":

        return process_pdf_bytes(file_bytes)

    if extension in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif"
    }:

        return process_image_bytes(file_bytes)

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Supported formats: PDF, JPG, JPEG, PNG, WEBP, BMP, TIFF."
    )


# ---------------------------------------------------------
# INCOME EXTRACTION
# ---------------------------------------------------------

def extract_income(text: str) -> float | None:
    """
    Try to detect annual/family income from OCR text.
    """

    patterns = [

        r"(?:annual|yearly|family)?\s*income"
        r"\s*(?:is|:|-)?\s*(?:rs\.?|₹|inr)?"
        r"\s*([0-9][0-9,\s]*)",

        r"(?:rs\.?|₹|inr)"
        r"\s*([0-9][0-9,\s]*)"
        r"\s*(?:annual|yearly|per\s*annum)",

        r"(?:annual|yearly|family)\s+income"
        r".{0,30}?"
        r"(?:rs\.?|₹|inr)"
        r"\s*([0-9][0-9,\s]*)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        value = match.group(1)

        value = (
            value
            .replace(",", "")
            .replace(" ", "")
        )

        try:
            return float(value)
        except ValueError:
            continue

    return None


# ---------------------------------------------------------
# AGE / DOB EXTRACTION
# ---------------------------------------------------------

def extract_age(text: str) -> int | None:
    """
    Detect age directly, or compute it from a Date of Birth
    (common on Aadhaar cards, PAN cards, etc.).
    """

    age_match = re.search(
        r"age\s*(?:is|:|-)?\s*(\d{1,3})\s*(?:years?)?",
        text,
        re.IGNORECASE,
    )

    if age_match:
        try:
            value = int(age_match.group(1))
            if 0 < value <= 120:
                return value
        except ValueError:
            pass

    dob_match = re.search(
        r"(?:dob|date of birth)\s*(?:is|:|-)?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})",
        text,
        re.IGNORECASE,
    )

    if dob_match:
        from datetime import datetime

        raw = dob_match.group(1)
        formats = [
            "%d/%m/%Y", "%d-%m-%Y",
            "%Y-%m-%d", "%Y/%m/%d",
            "%d/%m/%y", "%d-%m-%y",
        ]

        for fmt in formats:
            try:
                dob = datetime.strptime(raw, fmt)
                today = datetime.today()
                age = today.year - dob.year - (
                    (today.month, today.day) < (dob.month, dob.day)
                )
                if 0 < age <= 120:
                    return age
            except ValueError:
                continue

    return None


# ---------------------------------------------------------
# GENDER EXTRACTION
# ---------------------------------------------------------

def extract_gender(text: str) -> str | None:
    """
    Detect gender from common Indian ID document phrasing.
    """

    if re.search(r"\bfemale\b", text, re.IGNORECASE):
        return "Female"

    if re.search(r"\bmale\b", text, re.IGNORECASE):
        return "Male"

    if re.search(r"\btransgender\b", text, re.IGNORECASE):
        return "Other"

    return None


# ---------------------------------------------------------
# SOCIAL CATEGORY EXTRACTION
# ---------------------------------------------------------

def extract_category(text: str) -> str | None:
    """
    Detect social category (General/OBC/SC/ST/EWS), typically found
    on caste certificates.
    """

    patterns = {
        "SC": r"\b(sc|scheduled caste)\b",
        "ST": r"\b(st|scheduled tribe)\b",
        "OBC": r"\b(obc|other backward class(?:es)?)\b",
        "EWS": r"\b(ews|economically weaker section)\b",
        "General": r"\b(general|unreserved)\b",
    }

    for category, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return category

    return None


# ---------------------------------------------------------
# STATE EXTRACTION
# ---------------------------------------------------------

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry",
    "Chandigarh",
]


def extract_state(text: str) -> str | None:
    """
    Detect an Indian state name mentioned anywhere in the OCR text
    (e.g. in an address block).
    """

    for state in INDIAN_STATES:
        if re.search(rf"\b{re.escape(state)}\b", text, re.IGNORECASE):
            return state

    return None


# ---------------------------------------------------------
# OCCUPATION EXTRACTION
# ---------------------------------------------------------

def extract_occupation(text: str) -> str | None:
    """
    Detect occupation from a clearly labelled field. Occupation isn't
    standardized across document types, so this only fires when a
    label is present rather than guessing from free text.
    """

    match = re.search(
        r"occupation\s*(?:is|:|-)?\s*([A-Za-z\s]{2,40})",
        text,
        re.IGNORECASE,
    )

    if match:
        value = match.group(1).strip().split("\n")[0].strip()
        if value:
            return value

    return None


# ---------------------------------------------------------
# DOCUMENT INFORMATION EXTRACTION
# ---------------------------------------------------------

def extract_document_information(
    full_text: str
) -> dict[str, Any]:
    """
    Extract useful structured information from OCR text.
    Fields that can't be confidently detected are returned as None so
    the frontend/API caller knows to prompt the user to fill them in
    manually instead of silently defaulting them.
    """

    return {
        "income": extract_income(full_text),
        "age": extract_age(full_text),
        "gender": extract_gender(full_text),
        "category": extract_category(full_text),
        "state": extract_state(full_text),
        "occupation": extract_occupation(full_text),
    }


# ---------------------------------------------------------
# COMPLETE OCR PIPELINE
# ---------------------------------------------------------

def process_document(
    file_bytes: bytes,
    filename: str
) -> dict[str, Any]:
    """
    Complete document OCR pipeline.

    Supports:
    - JPG
    - JPEG
    - PNG
    - WEBP
    - BMP
    - TIFF
    - PDF
    - Multi-page PDF
    """

    ocr_result = process_document_file(
        file_bytes,
        filename
    )

    extracted = extract_document_information(
        ocr_result["full_text"]
    )

    return {
        "filename": filename,
        "document_type": ocr_result["document_type"],
        "page_count": ocr_result["page_count"],
        "full_text": ocr_result["full_text"],
        "pages": ocr_result["pages"],
        "extracted": extracted,
    }
